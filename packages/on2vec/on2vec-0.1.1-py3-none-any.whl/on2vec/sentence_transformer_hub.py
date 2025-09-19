"""
HuggingFace Hub compatible Sentence Transformers with ontology integration.

This module creates proper sentence-transformers models that can be:
1. Saved with model.save()
2. Loaded with SentenceTransformer.load()
3. Uploaded to HuggingFace Hub
4. Used seamlessly with the sentence-transformers ecosystem
"""

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from sentence_transformers.models import Transformer, Pooling
from typing import Dict, List, Optional, Union, Tuple, Any, Set
import numpy as np
import polars as pl
import json
import logging
from pathlib import Path
import re
from collections import Counter

logger = logging.getLogger(__name__)


class OntologyFusionModule(nn.Module):
    """
    Sentence Transformers compatible module that adds ontology knowledge.

    This module is designed to be the final layer in a SentenceTransformer pipeline:
    [Transformer] -> [Pooling] -> [OntologyFusionModule] -> output
    """

    def __init__(
        self,
        ontology_embeddings_file: str,
        fusion_method: str = 'concat',
        top_k_matches: int = 3,
        structural_weight: float = 0.3,
        input_dim: int = 384,  # Expected input dimension from previous layer
        # New improved parameters
        use_keyword_matching: bool = True,
        relevance_threshold: float = 0.3,
        preserve_dimensions: bool = False
    ):
        super().__init__()

        self.fusion_method = fusion_method
        self.top_k_matches = top_k_matches
        self.structural_weight = structural_weight
        self.input_dim = input_dim

        # New improved parameters
        self.use_keyword_matching = use_keyword_matching
        self.relevance_threshold = relevance_threshold
        self.preserve_dimensions = preserve_dimensions

        # Initialize attributes
        self.node_ids = []
        self.text_embeddings = None
        self.structural_embeddings = None
        self.concept_descriptions = []
        self.structural_dim = None

        # New keyword matching attributes
        self.concept_keywords = []  # Keywords extracted from concept names
        self.keyword_to_concepts = {}  # Mapping from keywords to concept indices

        # Load ontology data
        if ontology_embeddings_file:
            self._load_ontology_embeddings(ontology_embeddings_file)
        self._init_fusion_layers()

        logger.info(f"Initialized OntologyFusionModule: {self.input_dim} -> {self.get_sentence_embedding_dimension()}")

    def _load_ontology_embeddings(self, embeddings_file: str):
        """Load ontology embeddings from parquet file."""
        logger.info(f"Loading ontology embeddings for HF model: {embeddings_file}")

        df = pl.read_parquet(embeddings_file)

        # Verify format
        required_cols = ['node_id', 'text_embedding', 'structural_embedding']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"File must contain {required_cols}, found: {df.columns}")

        # Extract data
        self.node_ids = df['node_id'].to_list()
        self.text_embeddings = np.stack(df['text_embedding'].to_list())
        self.structural_embeddings = np.stack(df['structural_embedding'].to_list())

        self.structural_dim = self.structural_embeddings.shape[1]

        # Create concept descriptions
        self.concept_descriptions = [
            self._iri_to_description(iri) for iri in self.node_ids
        ]

        # Build keyword index for improved matching
        if self.use_keyword_matching:
            self._build_keyword_index()

        logger.info(f"Loaded {len(self.node_ids)} concepts for HF integration")
        logger.info(f"Text embeddings: {self.text_embeddings.shape}")
        logger.info(f"Structural embeddings: {self.structural_embeddings.shape}")
        if self.use_keyword_matching:
            logger.info(f"Built keyword index with {len(self.keyword_to_concepts)} unique keywords")

    def _iri_to_description(self, iri: str) -> str:
        """Convert IRI to readable description."""
        import re
        # Extract meaningful part
        if '#' in iri:
            name = iri.split('#')[-1]
        elif '/' in iri:
            name = iri.split('/')[-1]
        else:
            name = iri

        # Clean up
        name = re.sub(r'_', ' ', name)
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name.lower()

    def _build_keyword_index(self):
        """Build keyword index for improved concept matching."""
        self.keyword_to_concepts = {}

        for idx, iri in enumerate(self.node_ids):
            # Extract meaningful keywords from IRI
            keywords = self._extract_keywords_from_iri(iri)
            self.concept_keywords.append(keywords)

            # Index keywords to concepts
            for keyword in keywords:
                if keyword not in self.keyword_to_concepts:
                    self.keyword_to_concepts[keyword] = []
                self.keyword_to_concepts[keyword].append(idx)

    def _extract_keywords_from_iri(self, iri: str) -> Set[str]:
        """Extract meaningful keywords from ontology IRI."""
        # Extract meaningful part
        if '#' in iri:
            name = iri.split('#')[-1]
        elif '/' in iri:
            name = iri.split('/')[-1]
        else:
            name = iri

        # Clean and split into keywords
        name = re.sub(r'[_\-]', ' ', name)
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)  # Split camelCase

        # Extract meaningful terms (length > 2, not just numbers)
        keywords = set()
        for term in name.split():
            term = term.lower().strip()
            if len(term) > 2 and not term.isdigit() and term.isalpha():
                keywords.add(term)

                # Add common biomedical variants
                if term.endswith('ase'):  # enzymes
                    keywords.add(term[:-3])
                elif term.endswith('tion'):  # processes
                    keywords.add(term[:-4])

        return keywords

    def _extract_keywords_from_text(self, text: str) -> Set[str]:
        """Extract meaningful keywords from input text."""
        # Simple but effective keyword extraction
        text = text.lower()

        # Split into words and filter
        words = re.findall(r'\b[a-z]{3,}\b', text)  # Only alphabetic words of length 3+

        # Remove common stop words (simple list for biomedical domain)
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
            'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
            'its', 'let', 'put', 'say', 'she', 'too', 'use'
        }

        meaningful_words = set()
        for word in words:
            if word not in stop_words and len(word) > 2:
                meaningful_words.add(word)

                # Add biomedical variants
                if word.endswith('s') and len(word) > 3:  # Remove plural
                    meaningful_words.add(word[:-1])

        return meaningful_words

    def _init_fusion_layers(self):
        """Initialize fusion layers based on method."""
        if self.structural_dim is None:
            # No ontology data, fall back to text-only
            self.output_dim = self.input_dim
            return

        if self.fusion_method == 'concat':
            if self.preserve_dimensions:
                # Project structural to text dimension and concatenate
                self.struct_proj = nn.Linear(self.structural_dim, self.input_dim)
                self.output_dim = self.input_dim * 2  # Still doubled, but more manageable
            else:
                self.output_dim = self.input_dim + self.structural_dim
        elif self.fusion_method == 'weighted_avg':
            # Project to common dimension
            common_dim = min(self.input_dim, self.structural_dim)
            self.text_proj = nn.Linear(self.input_dim, common_dim)
            self.struct_proj = nn.Linear(self.structural_dim, common_dim)
            self.output_dim = common_dim
        elif self.fusion_method == 'attention':
            hidden_dim = max(self.input_dim, self.structural_dim)
            self.text_proj = nn.Linear(self.input_dim, hidden_dim)
            self.struct_proj = nn.Linear(self.structural_dim, hidden_dim)
            self.attention = nn.MultiheadAttention(hidden_dim, num_heads=4, batch_first=True)
            self.output_proj = nn.Linear(hidden_dim, hidden_dim)
            self.output_dim = hidden_dim
        elif self.fusion_method == 'gated':
            # Gated fusion
            self.gate = nn.Sequential(
                nn.Linear(self.input_dim + self.structural_dim, 1),
                nn.Sigmoid()
            )
            common_dim = min(self.input_dim, self.structural_dim)
            self.text_proj = nn.Linear(self.input_dim, common_dim)
            self.struct_proj = nn.Linear(self.structural_dim, common_dim)
            self.output_dim = common_dim
        # New improved fusion methods
        elif self.fusion_method == 'adaptive_weighted':
            # Learnable relevance threshold and weights
            self.relevance_gate = nn.Sequential(
                nn.Linear(self.input_dim + self.structural_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 1),
                nn.Sigmoid()
            )

            if self.preserve_dimensions:
                # Project structural to text dimension
                self.struct_proj = nn.Linear(self.structural_dim, self.input_dim)
                self.fusion_weights = nn.Parameter(torch.tensor([0.8, 0.2]))  # Learnable weights
                self.output_dim = self.input_dim
            else:
                self.output_dim = self.input_dim + self.structural_dim

        elif self.fusion_method == 'residual':
            # Residual connection approach
            self.struct_proj = nn.Linear(self.structural_dim, self.input_dim)
            self.gate = nn.Sequential(
                nn.Linear(self.input_dim, 1),
                nn.Sigmoid()
            )
            self.output_dim = self.input_dim

        elif self.fusion_method == 'cross_attention':
            # Cross-attention between text and structure
            hidden_dim = self.input_dim
            self.cross_attn = nn.MultiheadAttention(
                hidden_dim, num_heads=4, batch_first=True
            )
            self.struct_proj = nn.Linear(self.structural_dim, hidden_dim)
            self.layer_norm = nn.LayerNorm(hidden_dim)
            self.output_dim = hidden_dim
        else:
            raise ValueError(f"Unknown fusion method: {self.fusion_method}")

    def get_sentence_embedding_dimension(self) -> int:
        """Return the output dimension of this module."""
        return self.output_dim

    def save(self, output_path: str):
        """Save the module (required for SentenceTransformers compatibility)."""
        import json
        import os

        os.makedirs(output_path, exist_ok=True)

        # Save module config
        config = {
            'fusion_method': self.fusion_method,
            'top_k_matches': self.top_k_matches,
            'structural_weight': self.structural_weight,
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'structural_dim': self.structural_dim
        }

        with open(os.path.join(output_path, 'config.json'), 'w') as f:
            json.dump(config, f, indent=2)

        # Save PyTorch state
        torch.save(self.state_dict(), os.path.join(output_path, 'pytorch_model.bin'))

        # Save ontology data (node IDs and embeddings) - convert numpy to lists for safer serialization
        ontology_data = {
            'node_ids': self.node_ids,
            'text_embeddings': self.text_embeddings.tolist() if self.text_embeddings is not None else None,
            'structural_embeddings': self.structural_embeddings.tolist() if self.structural_embeddings is not None else None,
            'concept_descriptions': self.concept_descriptions
        }

        # Use JSON for safer serialization of non-tensor data
        import json
        with open(os.path.join(output_path, 'ontology_data.json'), 'w') as f:
            json.dump(ontology_data, f)

    @staticmethod
    def load(input_path: str):
        """Load the module (required for SentenceTransformers compatibility)."""
        import json
        import os

        # Load config
        with open(os.path.join(input_path, 'config.json'), 'r') as f:
            config = json.load(f)

        # Create module with exact same configuration
        module = OntologyFusionModule(
            ontology_embeddings_file="",  # Will be overridden
            fusion_method=config['fusion_method'],
            top_k_matches=config['top_k_matches'],
            structural_weight=config['structural_weight'],
            input_dim=config['input_dim']
        )

        # Override with loaded ontology data
        with open(os.path.join(input_path, 'ontology_data.json'), 'r') as f:
            ontology_data = json.load(f)

        module.node_ids = ontology_data['node_ids']
        module.text_embeddings = np.array(ontology_data['text_embeddings']) if ontology_data['text_embeddings'] else None
        module.structural_embeddings = np.array(ontology_data['structural_embeddings']) if ontology_data['structural_embeddings'] else None
        module.concept_descriptions = ontology_data['concept_descriptions']
        module.structural_dim = config['structural_dim']

        # Re-initialize fusion layers with the correct structural_dim before loading state
        module._init_fusion_layers()

        # Load state dict with weights_only=False for compatibility
        state_dict_path = os.path.join(input_path, 'pytorch_model.bin')
        if os.path.exists(state_dict_path):
            try:
                state_dict = torch.load(state_dict_path, weights_only=False, map_location='cpu')

                # Filter out any unexpected keys that might come from different fusion methods
                model_state = module.state_dict()
                filtered_state_dict = {k: v for k, v in state_dict.items() if k in model_state}

                if len(filtered_state_dict) != len(state_dict):
                    logger.warning(f"Filtered out {len(state_dict) - len(filtered_state_dict)} unexpected keys from state dict")

                module.load_state_dict(filtered_state_dict, strict=False)

            except Exception as e:
                logger.warning(f"Could not load state dict: {e}. Module will be initialized with random weights.")

        return module

    def find_similar_concepts(self, text_embedding: torch.Tensor) -> List[Tuple[int, float]]:
        """Find ontology concepts similar to the given text embedding (legacy method)."""
        # Convert to numpy for similarity computation
        if isinstance(text_embedding, torch.Tensor):
            text_embedding = text_embedding.detach().cpu().numpy()

        # Compute similarities with concept text embeddings
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(text_embedding.reshape(1, -1), self.text_embeddings)[0]

        # Get top-k matches
        top_indices = np.argsort(similarities)[-self.top_k_matches:][::-1]
        return [(idx, similarities[idx]) for idx in top_indices]

    def find_relevant_concepts_by_keywords(self, text: str) -> List[Tuple[int, float]]:
        """Find concepts using keyword matching instead of text similarity (improved method)."""
        if not self.use_keyword_matching or not hasattr(self, 'keyword_to_concepts'):
            # Fallback to original method
            return []

        # Extract keywords from input text
        text_keywords = self._extract_keywords_from_text(text)

        if not text_keywords:
            return []

        # Find matching concepts
        concept_scores = Counter()

        for keyword in text_keywords:
            if keyword in self.keyword_to_concepts:
                for concept_idx in self.keyword_to_concepts[keyword]:
                    # Score based on keyword overlap
                    concept_keywords = self.concept_keywords[concept_idx]
                    overlap = len(text_keywords.intersection(concept_keywords))
                    concept_scores[concept_idx] += overlap / len(concept_keywords) if concept_keywords else 0

        # Filter by relevance threshold and limit results
        relevant_concepts = [
            (idx, score) for idx, score in concept_scores.items()
            if score >= self.relevance_threshold
        ]

        # Sort by relevance and take top concepts
        relevant_concepts.sort(key=lambda x: x[1], reverse=True)
        return relevant_concepts[:self.top_k_matches]

    def forward(self, features: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        Forward pass compatible with SentenceTransformers.

        Args:
            features: Dictionary with 'sentence_embedding' key from previous layer

        Returns:
            Dictionary with updated 'sentence_embedding' key
        """
        # Get text embeddings from previous layer (usually Pooling)
        text_embeddings = features['sentence_embedding']  # [batch_size, input_dim]
        batch_size = text_embeddings.shape[0]

        # If no structural embeddings available, return text embeddings as-is
        if self.structural_dim is None:
            return features

        # Process each sentence in the batch
        structural_embeddings_list = []

        for i in range(batch_size):
            text_embed = text_embeddings[i]  # [input_dim]

            # Use improved concept matching if available
            if self.use_keyword_matching:
                # We need access to original text for keyword matching
                # This is a limitation - in practice, you'd need to store the input text
                # For now, fall back to similarity-based matching with relevance filtering
                similar_concepts = self.find_similar_concepts(text_embed)

                # Apply relevance threshold filtering to similarity-based results
                similar_concepts = [(idx, score) for idx, score in similar_concepts
                                  if score >= self.relevance_threshold]
            else:
                # Use original similarity-based matching
                similar_concepts = self.find_similar_concepts(text_embed)

            if similar_concepts:
                indices, scores = zip(*similar_concepts)

                # Get structural embeddings for matched concepts
                struct_embeds = self.structural_embeddings[list(indices)]  # [top_k, structural_dim]

                # Weight by similarity scores
                scores = np.array(scores)
                scores_sum = scores.sum()
                if scores_sum > 0:
                    weights = scores / scores_sum  # Normalize weights
                else:
                    # If all scores are 0, use uniform weights
                    weights = np.ones(len(scores)) / len(scores)

                # Weighted average of structural embeddings
                weighted_struct = np.average(struct_embeds, axis=0, weights=weights)
                structural_embeddings_list.append(weighted_struct)
            else:
                # No matches, use zero embedding
                structural_embeddings_list.append(np.zeros(self.structural_dim))

        # Convert to tensor
        structural_embeddings = torch.tensor(
            np.stack(structural_embeddings_list),
            dtype=torch.float32,
            device=text_embeddings.device
        )

        # Fuse embeddings based on method
        fused_embeddings = self._fuse_embeddings(text_embeddings, structural_embeddings)

        # Update features dictionary (SentenceTransformers convention)
        features['sentence_embedding'] = fused_embeddings
        return features

    def _fuse_embeddings(self, text_embeds: torch.Tensor, struct_embeds: torch.Tensor) -> torch.Tensor:
        """Fuse text and structural embeddings."""
        if self.fusion_method == 'concat':
            if self.preserve_dimensions and hasattr(self, 'struct_proj'):
                struct_proj = self.struct_proj(struct_embeds)
                return torch.cat([text_embeds, struct_proj], dim=1)
            else:
                return torch.cat([text_embeds, struct_embeds], dim=1)

        elif self.fusion_method == 'weighted_avg':
            text_proj = self.text_proj(text_embeds)
            struct_proj = self.struct_proj(struct_embeds)
            return (1 - self.structural_weight) * text_proj + self.structural_weight * struct_proj

        elif self.fusion_method == 'attention':
            text_proj = self.text_proj(text_embeds).unsqueeze(1)  # [batch, 1, hidden]
            struct_proj = self.struct_proj(struct_embeds).unsqueeze(1)  # [batch, 1, hidden]

            # Concatenate for attention
            combined = torch.cat([text_proj, struct_proj], dim=1)  # [batch, 2, hidden]

            # Apply attention
            attn_output, _ = self.attention(combined, combined, combined)
            pooled = attn_output.mean(dim=1)  # [batch, hidden]

            return self.output_proj(pooled)

        elif self.fusion_method == 'gated':
            # Learn gate weights
            combined_input = torch.cat([text_embeds, struct_embeds], dim=1)
            gate_weights = self.gate(combined_input)

            # Project to common dimension
            text_proj = self.text_proj(text_embeds)
            struct_proj = self.struct_proj(struct_embeds)

            # Gated combination
            return gate_weights * text_proj + (1 - gate_weights) * struct_proj

        # New improved fusion methods
        elif self.fusion_method == 'adaptive_weighted':
            if self.preserve_dimensions:
                # Project structural to text dimension
                struct_proj = self.struct_proj(struct_embeds)

                # Learn relevance gate
                combined = torch.cat([text_embeds, struct_embeds], dim=1)
                relevance = self.relevance_gate(combined)  # [batch, 1]

                # Adaptive weighting based on relevance
                weights = torch.softmax(self.fusion_weights, dim=0)
                base_weight = weights[0] + relevance.squeeze() * (weights[1] - weights[0])
                struct_weight = 1 - base_weight

                return base_weight.unsqueeze(1) * text_embeds + struct_weight.unsqueeze(1) * struct_proj
            else:
                return torch.cat([text_embeds, struct_embeds], dim=1)

        elif self.fusion_method == 'residual':
            # Residual connection with learned gate
            struct_proj = self.struct_proj(struct_embeds)
            gate = self.gate(text_embeds)
            return text_embeds + gate * struct_proj

        elif self.fusion_method == 'cross_attention':
            # Cross-attention fusion
            struct_proj = self.struct_proj(struct_embeds).unsqueeze(1)  # [batch, 1, dim]
            text_query = text_embeds.unsqueeze(1)  # [batch, 1, dim]

            # Cross-attention: text attends to structure
            attended, _ = self.cross_attn(text_query, struct_proj, struct_proj)
            attended = attended.squeeze(1)  # [batch, dim]

            # Residual connection with layer norm
            return self.layer_norm(text_embeds + attended)

        else:
            raise ValueError(f"Unknown fusion method: {self.fusion_method}")


def create_hf_sentence_transformer(
    ontology_embeddings_file: str,
    base_model: str = 'all-MiniLM-L6-v2',
    fusion_method: str = 'concat',
    top_k_matches: int = 3,
    structural_weight: float = 0.3,
    model_name: str = "ontology-augmented-model",
    # New improved parameters
    use_keyword_matching: bool = True,
    relevance_threshold: float = 0.3,
    preserve_dimensions: bool = False
) -> SentenceTransformer:
    """
    Create a HuggingFace Hub compatible SentenceTransformer with ontology integration.

    Args:
        ontology_embeddings_file: Path to on2vec generated parquet file
        base_model: Base transformer model name
        fusion_method: How to combine embeddings ('concat', 'weighted_avg', 'attention', 'gated',
                      'adaptive_weighted', 'residual', 'cross_attention')
        top_k_matches: Number of ontology concepts to match
        structural_weight: Weight for structural embeddings
        model_name: Name for the model
        use_keyword_matching: Use improved keyword-based concept matching
        relevance_threshold: Minimum relevance score for concept matching
        preserve_dimensions: Keep output dimensions same as input

    Returns:
        SentenceTransformer model ready for Hub upload
    """
    logger.info(f"Creating HuggingFace compatible model: {model_name}")

    # Create transformer and pooling layers
    try:
        transformer = Transformer(base_model)
    except Exception as e:
        logger.error(f"Failed to load transformer {base_model}: {e}")
        # Fallback: try loading as SentenceTransformer first
        temp_model = SentenceTransformer(base_model)
        transformer = temp_model[0]  # Get the transformer component

    pooling = Pooling(
        transformer.get_word_embedding_dimension(),
        pooling_mode='mean'
    )

    # Create ontology fusion module
    ontology_module = OntologyFusionModule(
        ontology_embeddings_file=ontology_embeddings_file,
        fusion_method=fusion_method,
        top_k_matches=top_k_matches,
        structural_weight=structural_weight,
        input_dim=transformer.get_word_embedding_dimension(),
        use_keyword_matching=use_keyword_matching,
        relevance_threshold=relevance_threshold,
        preserve_dimensions=preserve_dimensions
    )

    # Create the full pipeline
    model = SentenceTransformer(
        modules=[transformer, pooling, ontology_module],
        device='cpu'  # Start on CPU for compatibility
    )

    # Add metadata for the Hub
    model._model_card_text = f"""
# {model_name}

This is a sentence-transformers model that combines semantic text similarity with ontology structural knowledge using on2vec embeddings.

## Model Details
- **Base Model**: {base_model}
- **Fusion Method**: {fusion_method}
- **Ontology Concepts**: {len(ontology_module.node_ids):,}
- **Output Dimensions**: {ontology_module.get_sentence_embedding_dimension()}

## Usage

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('{model_name}')
embeddings = model.encode(['heart disease', 'cardiovascular problems'])
```

## Architecture
1. **Transformer**: {base_model} for text encoding
2. **Pooling**: Mean pooling of token embeddings
3. **Ontology Fusion**: Combines text with structural knowledge from ontology

## Training Data
- Ontology embeddings generated using on2vec
- Text features from {base_model}
- Structural features from graph neural networks
"""

    logger.info(f"Created model with {ontology_module.get_sentence_embedding_dimension()} output dimensions")
    return model


def create_and_save_hf_model(
    ontology_embeddings_file: str,
    model_name: str,
    output_dir: str,
    base_model: str = 'all-MiniLM-L6-v2',
    fusion_method: str = 'concat',
    # New improved parameters
    use_keyword_matching: bool = True,
    relevance_threshold: float = 0.3,
    preserve_dimensions: bool = False
) -> str:
    """
    Create and save a HuggingFace compatible model.

    Args:
        ontology_embeddings_file: Path to embeddings parquet
        model_name: Name for the model
        output_dir: Directory to save the model
        base_model: Base transformer model
        fusion_method: Fusion method to use

    Returns:
        Path to saved model directory
    """
    model = create_hf_sentence_transformer(
        ontology_embeddings_file=ontology_embeddings_file,
        base_model=base_model,
        fusion_method=fusion_method,
        model_name=model_name,
        use_keyword_matching=use_keyword_matching,
        relevance_threshold=relevance_threshold,
        preserve_dimensions=preserve_dimensions
    )

    # Save model
    model_path = Path(output_dir) / model_name
    model_path.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))

    # Create additional metadata files
    _create_model_metadata(model_path, ontology_embeddings_file, base_model, fusion_method)

    logger.info(f"Model saved to: {model_path}")
    return str(model_path)


def _create_model_metadata(model_path: Path, embeddings_file: str, base_model: str, fusion_method: str):
    """Create additional metadata files for the model."""

    # Load embeddings metadata
    try:
        df = pl.read_parquet(embeddings_file)
        metadata = df.get_column('metadata').to_list()[0] if 'metadata' in df.columns else {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
    except Exception:
        metadata = {}

    # Create on2vec specific metadata
    on2vec_metadata = {
        "on2vec_version": "1.0.0",
        "ontology_source": embeddings_file,
        "base_model": base_model,
        "fusion_method": fusion_method,
        "ontology_concepts": len(df) if 'df' in locals() else "unknown",
        "creation_timestamp": str(torch.utils.data.get_worker_info()),
        "source_metadata": metadata
    }

    # Save metadata
    metadata_file = model_path / "on2vec_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(on2vec_metadata, f, indent=2)

    # Create README with usage examples
    readme_content = f"""
# Ontology-Augmented Sentence Transformer

This model combines the semantic understanding of `{base_model}` with structural knowledge from ontology embeddings.

## Quick Start

```python
from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer("{model_path.name}")

# Encode sentences
sentences = ["heart disease", "cardiovascular problems", "protein folding"]
embeddings = model.encode(sentences)

# Compute similarities
from sentence_transformers.util import cos_sim
similarities = cos_sim(embeddings, embeddings)
print(similarities)
```

## Model Architecture

- **Base**: {base_model}
- **Fusion**: {fusion_method}
- **Output Dimensions**: Combined text + structural embeddings

## Use Cases

- Biomedical text similarity
- Concept clustering with domain knowledge
- Semantic search with ontology awareness
- Document retrieval in specialized domains

## Citation

If you use this model, please cite:

```
@software{{on2vec_sentence_transformers,
  title={{Ontology-Augmented Sentence Transformers}},
  author={{on2vec}},
  year={{2025}},
  url={{https://github.com/your-repo/on2vec}}
}}
```
"""

    readme_file = model_path / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)


# Example usage and testing functions
def test_hf_model_creation():
    """Test function to verify HF model creation works."""
    print("Testing HuggingFace model creation...")

    # This would use your actual embeddings file
    embeddings_file = "test_embeddings.parquet"

    if not Path(embeddings_file).exists():
        print(f"Embeddings file not found: {embeddings_file}")
        print("Run: python main.py ontology.owl --use_text_features --output test_embeddings.parquet")
        return

    # Create model
    model = create_hf_sentence_transformer(
        ontology_embeddings_file=embeddings_file,
        fusion_method='concat',
        model_name="test-ontology-model"
    )

    # Test encoding
    sentences = ["heart disease", "cardiovascular problems", "protein folding"]
    embeddings = model.encode(sentences)

    print(f"Model created successfully!")
    print(f"Output shape: {embeddings.shape}")
    print(f"Model architecture: {len(model._modules)} modules")

    # Test saving and loading
    test_dir = "./test_hf_model"
    model.save(test_dir)
    print(f"Model saved to: {test_dir}")

    # Test loading
    loaded_model = SentenceTransformer(test_dir)
    loaded_embeddings = loaded_model.encode(sentences)

    # Verify consistency
    import numpy as np
    if np.allclose(embeddings, loaded_embeddings):
        print("✅ Model save/load test passed!")
    else:
        print("❌ Model save/load test failed!")


if __name__ == "__main__":
    test_hf_model_creation()