# ENCDR - Neural Component Dimensionality Reduction

A Python library for autoencoder-based dimensionality reduction with a scikit-learn compatible interface.

## Features

- **Scikit-learn Compatible**: Implements `fit()`, `transform()`, `predict()`, and `fit_transform()` methods
- **PyTorch Lightning Backend**: Deep learning framework with automatic GPU support
- **Specialized Autoencoder Variants**: Variational (VENCDR), Denoising (DENCDR), and Sparse (SENCDR) autoencoders
- **Configurable Architecture**: Customizable encoder/decoder layers, activation functions, and training parameters
- **Automatic Standardization**: Optional feature scaling for improved training stability
- **Validation Support**: Built-in train/validation splits for monitoring training progress
- **Multiple Activation Functions**: Support for ReLU, Tanh, Sigmoid, LeakyReLU, ELU, and GELU
- **Model Persistence**: Save and load trained models with full state preservation

## Installation

```bash
uv add encdr
# or
pip install encdr
```

## Dependencies

- Python ≥ 3.12
- PyTorch Lightning ≥ 2.5.5
- scikit-learn ≥ 1.7.2
- torch ≥ 2.0.0
- numpy ≥ 1.21.0

## Quick Start

```python
from encdr import ENCDR, VENCDR, DENCDR, SENCDR
from sklearn.datasets import make_classification
import numpy as np

# Generate sample data
X, _ = make_classification(n_samples=1000, n_features=50, n_informative=30, random_state=42)

# Create and train autoencoder
encdr = ENCDR(
    hidden_dims=[64, 32, 16],  # Encoder layer sizes
    latent_dim=8,              # Bottleneck dimension
    max_epochs=50,             # Training epochs
    random_state=42
)

# Fit and transform data
X_reduced = encdr.fit_transform(X)
print(f"Original shape: {X.shape}, Reduced shape: {X_reduced.shape}")

# Reconstruct original data
X_reconstructed = encdr.predict(X)
reconstruction_error = np.mean((X - X_reconstructed) ** 2)
print(f"Reconstruction MSE: {reconstruction_error:.4f}")

# Save model for later use
encdr.save("my_autoencoder.pkl")

# Load model (in a different session)
loaded_encdr = ENCDR.load("my_autoencoder.pkl")
X_reduced_loaded = loaded_encdr.transform(X[:10])  # Same results as original model
```

## Advanced Usage

### Custom Architecture

```python
encdr = ENCDR(
    hidden_dims=[128, 64, 32, 16],     # Deep architecture
    latent_dim=10,                     # 10D latent space
    activation="tanh",                 # Tanh activation
    dropout_rate=0.2,                  # 20% dropout for regularization
    learning_rate=1e-3,                # Learning rate
    weight_decay=1e-4,                 # L2 regularization
    batch_size=64,                     # Batch size
    max_epochs=100,                    # Training epochs
    validation_split=0.2,              # 20% validation split
    standardize=True,                  # Feature standardization
    random_state=42,                   # Reproducibility
    trainer_kwargs={"accelerator": "gpu", "devices": 1}  # GPU training
)
```

### Integration with Scikit-learn Pipelines

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('encdr', ENCDR(latent_dim=5, max_epochs=50, standardize=False))
])

# Split data
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

# Fit pipeline and transform
X_train_reduced = pipeline.fit_transform(X_train)
X_test_reduced = pipeline.transform(X_test)
```

### Dimensionality Reduction Workflow

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

# Load iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Reduce to 2D for visualization
encdr = ENCDR(latent_dim=2, max_epochs=100, random_state=42)
X_2d = encdr.fit_transform(X)

# Plot results
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.scatter(X_2d[:, 0], X_2d[:, 1], c=y, cmap='viridis')
plt.title('ENCDR: Iris Dataset (2D)')
plt.xlabel('Component 1')
plt.ylabel('Component 2')

# Compare reconstruction quality
X_reconstructed = encdr.predict(X)
mse_per_feature = np.mean((X - X_reconstructed) ** 2, axis=0)

plt.subplot(1, 2, 2)
plt.bar(range(len(mse_per_feature)), mse_per_feature)
plt.title('Reconstruction Error by Feature')
plt.xlabel('Feature Index')
plt.ylabel('MSE')

plt.tight_layout()
plt.show()
```

## Specialized Autoencoder Variants

ENCDR provides three specialized autoencoder variants for different use cases:

### VENCDR - Variational Autoencoder

VENCDR implements a Variational Autoencoder (VAE) for probabilistic dimensionality reduction and generative modeling.

```python
from encdr import VENCDR
import numpy as np

# Create VAE with custom beta parameter
vae = VENCDR(
    hidden_dims=[64, 32],
    latent_dim=8,
    beta=1.0,           # KL divergence weight (beta-VAE)
    max_epochs=50,
    random_state=42
)

# Fit the model
vae.fit(X)

# Deterministic transform using mean of latent distribution
X_mean = vae.transform(X, use_mean=True)

# Stochastic transform by sampling from latent distribution
X_sample = vae.transform(X, use_mean=False)

# Generate new samples from the learned distribution
generated_samples = vae.sample(num_samples=100)

print(f"Generated samples shape: {generated_samples.shape}")
```

**Key Features:**
- Probabilistic latent space with mean and variance
- Generative sampling capabilities
- Configurable β parameter for β-VAE
- Both deterministic and stochastic transformations

### DENCDR - Denoising Autoencoder

DENCDR implements a Denoising Autoencoder for robust feature learning and noise removal.

```python
from encdr import DENCDR
import numpy as np

# Create denoising autoencoder
dae = DENCDR(
    hidden_dims=[64, 32],
    latent_dim=8,
    noise_factor=0.2,        # Amount of noise to add during training
    noise_type='gaussian',   # Type of noise ('gaussian', 'uniform', 'masking')
    max_epochs=50,
    random_state=42
)

# Fit the model (trains on noisy inputs, reconstructs clean outputs)
dae.fit(X)

# Transform to latent space
X_latent = dae.transform(X)

# Denoise noisy data
noise = np.random.normal(0, 0.1, X.shape)
X_noisy = X + noise
X_denoised = dae.denoise(X_noisy)

# Compare reconstruction quality
print(f"Original MSE: {np.mean((X - X_noisy)**2):.4f}")
print(f"Denoised MSE: {np.mean((X - X_denoised)**2):.4f}")
```

**Key Features:**
- Robust to input noise
- Multiple noise types (Gaussian, uniform, masking)
- Dedicated `denoise()` method for cleaning noisy data
- Learns more generalizable representations

### SENCDR - Sparse Autoencoder

SENCDR implements a Sparse Autoencoder for learning sparse, interpretable representations.

```python
from encdr import SENCDR
import numpy as np

# Create sparse autoencoder
sae = SENCDR(
    hidden_dims=[64, 32],
    latent_dim=8,
    sparsity_weight=1e-3,    # Weight for sparsity penalty
    sparsity_target=0.05,    # Target average activation
    sparsity_type='kl',      # Sparsity penalty type ('kl', 'l1', 'l2')
    max_epochs=50,
    random_state=42
)

# Fit the model
sae.fit(X)

# Transform with automatic thresholding for sparsity
X_sparse = sae.transform(X, apply_threshold=True, threshold=1e-3)

# Get sparse features (explicitly thresholded)
X_sparse_features = sae.get_sparse_features(X, threshold=1e-3)

# Analyze sparsity metrics
metrics = sae.sparsity_metrics(X)
print(f"Sparsity ratio: {metrics['sparsity_ratio']:.3f}")
print(f"Mean activation: {metrics['mean_activation']:.3f}")
print(f"Active neurons: {metrics['active_neurons']:.1f}")
```

**Key Features:**
- Learns sparse, interpretable representations
- Multiple sparsity penalty types (KL divergence, L1, L2)
- Configurable sparsity targets and weights
- Built-in sparsity analysis tools

### Choosing the Right Variant

- **ENCDR**: Standard autoencoder for general dimensionality reduction
- **VENCDR**: When you need probabilistic representations or generative capabilities
- **DENCDR**: When your data is noisy or you want robust feature learning
- **SENCDR**: When you need sparse, interpretable features for analysis

## API Reference

### ENCDR Class

#### Parameters

- **hidden_dims** (list of int, default=[64, 32]): Hidden layer dimensions for encoder
- **latent_dim** (int, default=10): Dimension of latent space
- **learning_rate** (float, default=1e-3): Learning rate for optimization
- **activation** (str, default='relu'): Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu', 'elu', 'gelu')
- **dropout_rate** (float, default=0.0): Dropout rate for regularization
- **weight_decay** (float, default=0.0): L2 regularization weight decay
- **batch_size** (int, default=32): Training batch size
- **max_epochs** (int, default=100): Maximum training epochs
- **validation_split** (float, default=0.2): Fraction of data for validation
- **standardize** (bool, default=True): Whether to standardize features
- **random_state** (int, optional): Random seed for reproducibility
- **trainer_kwargs** (dict, optional): Additional PyTorch Lightning Trainer arguments

#### Methods

- **fit(X, y=None)**: Train the autoencoder on data X
- **transform(X)**: Transform data to latent representation
- **fit_transform(X, y=None)**: Fit and transform in one step
- **inverse_transform(X)**: Reconstruct data from latent representation
- **predict(X)**: Reconstruct input data (alias for encode→decode)
- **score(X, y=None)**: Return negative reconstruction MSE
- **save(filepath)**: Save fitted model to disk
- **load(filepath)**: Load saved model from disk (class method)

### VENCDR Class (Variational Autoencoder)

Extends ENCDR with variational autoencoder capabilities for probabilistic dimensionality reduction.

#### Additional Parameters

- **beta** (float, default=1.0): Weight for KL divergence term in loss function (β-VAE parameter)

#### Additional Methods

- **transform(X, use_mean=True)**: Transform data to latent space
  - `use_mean=True`: Use mean of latent distribution (deterministic)
  - `use_mean=False`: Sample from latent distribution (stochastic)
- **sample(num_samples)**: Generate new samples from learned latent distribution

#### Example Usage

```python
from encdr import VENCDR

# Create and fit VAE
vae = VENCDR(latent_dim=5, beta=1.5, max_epochs=50)
vae.fit(X_train)

# Deterministic encoding
X_deterministic = vae.transform(X_test, use_mean=True)

# Stochastic encoding (different results each time)
X_stochastic1 = vae.transform(X_test, use_mean=False)
X_stochastic2 = vae.transform(X_test, use_mean=False)

# Generate new samples
new_samples = vae.sample(num_samples=50)
```

### DENCDR Class (Denoising Autoencoder)

Extends ENCDR with denoising capabilities for robust feature learning.

#### Additional Parameters

- **noise_factor** (float, default=0.1): Amount of noise to add during training
- **noise_type** (str, default='gaussian'): Type of noise ('gaussian', 'uniform', 'masking')

#### Additional Methods

- **denoise(X)**: Remove noise from input data using the trained autoencoder

#### Example Usage

```python
from encdr import DENCDR
import numpy as np

# Create and fit denoising autoencoder
dae = DENCDR(noise_factor=0.2, noise_type='gaussian', max_epochs=50)
dae.fit(X_train)

# Denoise corrupted data
noise = np.random.normal(0, 0.1, X_test.shape)
X_noisy = X_test + noise
X_clean = dae.denoise(X_noisy)

# Regular dimensionality reduction also works
X_latent = dae.transform(X_test)
```

### SENCDR Class (Sparse Autoencoder)

Extends ENCDR with sparsity constraints for learning interpretable representations.

#### Additional Parameters

- **sparsity_weight** (float, default=1e-3): Weight for sparsity penalty in loss function
- **sparsity_target** (float, default=0.05): Target average activation for sparsity constraint
- **sparsity_type** (str, default='kl'): Type of sparsity penalty ('kl', 'l1', 'l2')

#### Additional Methods

- **transform(X, apply_threshold=False, threshold=1e-3)**: Transform with optional thresholding
- **get_sparse_features(X, threshold=1e-3)**: Get explicitly thresholded sparse features
- **sparsity_metrics(X)**: Compute sparsity analysis metrics

#### Example Usage

```python
from encdr import SENCDR

# Create and fit sparse autoencoder
sae = SENCDR(
    sparsity_weight=1e-3, 
    sparsity_target=0.1, 
    sparsity_type='l1',
    max_epochs=50
)
sae.fit(X_train)

# Get sparse representation
X_sparse = sae.transform(X_test, apply_threshold=True, threshold=1e-3)

# Analyze sparsity
metrics = sae.sparsity_metrics(X_test)
print(f"Sparsity ratio: {metrics['sparsity_ratio']}")
print(f"Mean activation: {metrics['mean_activation']}")
print(f"Active neurons per sample: {metrics['active_neurons']}")
```

## Comparative Examples

Here's how to compare different autoencoder variants on the same dataset:

```python
from encdr import ENCDR, VENCDR, DENCDR, SENCDR
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

# Generate sample dataset
X, y = make_classification(
    n_samples=1000, n_features=50, n_informative=30, 
    n_redundant=10, noise=0.1, random_state=42
)
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

# Common parameters
common_params = {
    'hidden_dims': [64, 32],
    'latent_dim': 8,
    'max_epochs': 50,
    'random_state': 42
}

# Train different autoencoder variants
models = {
    'Standard': ENCDR(**common_params),
    'Variational': VENCDR(**common_params, beta=1.0),
    'Denoising': DENCDR(**common_params, noise_factor=0.1),
    'Sparse': SENCDR(**common_params, sparsity_weight=1e-3)
}

# Fit all models and evaluate
results = {}
for name, model in models.items():
    print(f"Training {name} autoencoder...")
    model.fit(X_train)
    
    # Evaluate reconstruction quality
    X_pred = model.predict(X_test)
    mse = np.mean((X_test - X_pred) ** 2)
    
    # Get latent representations
    X_latent = model.transform(X_test)
    
    results[name] = {
        'mse': mse,
        'latent_std': np.std(X_latent),
        'model': model
    }
    
    print(f"{name} - MSE: {mse:.4f}, Latent std: {np.std(X_latent):.4f}")

# Visualize latent representations (if 2D)
if common_params['latent_dim'] == 2:
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()
    
    for i, (name, result) in enumerate(results.items()):
        X_2d = result['model'].transform(X_test)
        axes[i].scatter(X_2d[:, 0], X_2d[:, 1], c=y[len(X_train):], cmap='viridis', alpha=0.7)
        axes[i].set_title(f'{name} Autoencoder (MSE: {result["mse"]:.4f})')
        axes[i].set_xlabel('Latent Dim 1')
        axes[i].set_ylabel('Latent Dim 2')
    
    plt.tight_layout()
    plt.show()
```

### Specialized Use Cases

#### Generative Modeling with VENCDR

```python
# Train VAE for generation
vae = VENCDR(latent_dim=10, beta=1.0, max_epochs=100)
vae.fit(X_train)

# Generate new samples similar to training data
generated = vae.sample(num_samples=200)

# Interpolate between two data points in latent space
z1 = vae.transform(X_test[0:1], use_mean=True)
z2 = vae.transform(X_test[1:2], use_mean=True)

# Create interpolation
alphas = np.linspace(0, 1, 10)
interpolations = []
for alpha in alphas:
    z_interp = (1 - alpha) * z1 + alpha * z2
    x_interp = vae.inverse_transform(z_interp)
    interpolations.append(x_interp[0])

interpolations = np.array(interpolations)
print(f"Interpolation shape: {interpolations.shape}")
```

#### Noise Robustness with DENCDR

```python
# Train denoising autoencoder
dae = DENCDR(noise_factor=0.2, noise_type='gaussian', max_epochs=100)
dae.fit(X_train)

# Test with different noise levels
noise_levels = [0.05, 0.1, 0.2, 0.3]
denoising_performance = []

for noise_level in noise_levels:
    # Add noise
    noise = np.random.normal(0, noise_level, X_test.shape)
    X_noisy = X_test + noise
    
    # Denoise
    X_denoised = dae.denoise(X_noisy)
    
    # Measure improvement
    noisy_mse = np.mean((X_test - X_noisy) ** 2)
    denoised_mse = np.mean((X_test - X_denoised) ** 2)
    improvement = (noisy_mse - denoised_mse) / noisy_mse
    
    denoising_performance.append(improvement)
    print(f"Noise level {noise_level}: {improvement:.1%} improvement")
```

#### Feature Analysis with SENCDR

```python
# Train sparse autoencoder
sae = SENCDR(
    sparsity_weight=1e-2, 
    sparsity_target=0.1, 
    sparsity_type='l1',
    max_epochs=100
)
sae.fit(X_train)

# Analyze feature importance
X_sparse = sae.get_sparse_features(X_test, threshold=1e-3)
feature_usage = np.mean(X_sparse != 0, axis=0)

# Find most important latent features
important_features = np.argsort(feature_usage)[::-1][:5]
print(f"Most active latent features: {important_features}")
print(f"Usage rates: {feature_usage[important_features]}")

# Get sparsity metrics
metrics = sae.sparsity_metrics(X_test)
print(f"\nSparsity Analysis:")
for key, value in metrics.items():
    print(f"{key}: {value:.4f}")
```

## Model Persistence

All ENCDR variants support saving and loading trained models for later use. This includes all model parameters, weights, and preprocessing state (such as the fitted scaler).

### Saving Models

```python
# Train different types of models
encdr = ENCDR(hidden_dims=[64, 32], latent_dim=8, max_epochs=50)
vae = VENCDR(hidden_dims=[64, 32], latent_dim=8, beta=1.5, max_epochs=50)
dae = DENCDR(hidden_dims=[64, 32], latent_dim=8, noise_factor=0.2, max_epochs=50)
sae = SENCDR(hidden_dims=[64, 32], latent_dim=8, sparsity_weight=1e-3, max_epochs=50)

# Fit the models
for model in [encdr, vae, dae, sae]:
    model.fit(X_train)

# Save each model with descriptive names
encdr.save("standard_autoencoder.pkl")
vae.save("variational_autoencoder.pkl")
dae.save("denoising_autoencoder.pkl")
sae.save("sparse_autoencoder.pkl")

# Models can also be saved to specific directories
vae.save("/path/to/models/vae_model")  # .pkl extension added automatically
```

### Loading Models

```python
# Load previously saved models (class-specific loading)
loaded_encdr = ENCDR.load("standard_autoencoder.pkl")
loaded_vae = VENCDR.load("variational_autoencoder.pkl")
loaded_dae = DENCDR.load("denoising_autoencoder.pkl")
loaded_sae = SENCDR.load("sparse_autoencoder.pkl")

# All loaded models retain their specialized functionality
X_transformed = loaded_encdr.transform(X_test)
X_sampled = loaded_vae.transform(X_test, use_mean=False)  # Stochastic sampling
X_denoised = loaded_dae.denoise(X_test)
sparsity_metrics = loaded_sae.sparsity_metrics(X_test)

# Original parameters are preserved
print(f"VAE beta parameter: {loaded_vae.beta}")
print(f"DAE noise factor: {loaded_dae.noise_factor}")
print(f"SAE sparsity weight: {loaded_sae.sparsity_weight}")

# All models maintain scikit-learn compatibility
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Create pipeline with loaded model
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('autoencoder', loaded_vae)
])

# Use in pipeline
X_pipeline_result = pipeline.fit_transform(X_train)
```
