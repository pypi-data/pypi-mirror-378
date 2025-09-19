"""
PyTorch Lightning autoencoder model for dimensionality reduction.
"""

from typing import List, Optional, Union

import lightning as L
import torch
import torch.nn as nn
import torch.nn.functional as F


class AutoEncoder(L.LightningModule):
    """
    A configurable autoencoder model using PyTorch Lightning.

    This model supports various architectures with customizable layers,
    activation functions, and training parameters.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        latent_dim: int,
        learning_rate: float = 1e-3,
        activation: str = "relu",
        dropout_rate: float = 0.0,
        weight_decay: float = 0.0,
    ):
        """
        Initialize the autoencoder.

        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions for encoder
            latent_dim: Dimension of the latent (bottleneck) layer
            learning_rate: Learning rate for optimization
            activation: Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu')
            dropout_rate: Dropout rate for regularization
            weight_decay: L2 regularization weight decay
        """
        super().__init__()
        self.save_hyperparameters()

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.weight_decay = weight_decay

        # Get activation function
        self.activation_fn = self._get_activation_function(activation)

        # Build encoder
        encoder_layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            encoder_layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation_fn,
                    nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                ]
            )
            prev_dim = hidden_dim

        # Add final layer to latent space
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)

        # Build decoder (mirror of encoder)
        decoder_layers = []
        prev_dim = latent_dim

        # Reverse the hidden dimensions for decoder
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation_fn,
                    nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                ]
            )
            prev_dim = hidden_dim

        # Add final reconstruction layer
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def _get_activation_function(self, activation: str) -> nn.Module:
        """Get activation function by name."""
        activation_map = {
            "relu": nn.ReLU(),
            "tanh": nn.Tanh(),
            "sigmoid": nn.Sigmoid(),
            "leaky_relu": nn.LeakyReLU(),
            "elu": nn.ELU(),
            "gelu": nn.GELU(),
        }

        if activation.lower() not in activation_map:
            raise ValueError(f"Unsupported activation function: {activation}")

        return activation_map[activation.lower()]

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        return self.encoder(x)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to reconstruction."""
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through autoencoder."""
        z = self.encode(x)
        reconstruction = self.decode(z)
        return reconstruction

    def training_step(self, batch, batch_idx):
        """Training step for PyTorch Lightning."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        x_hat = self(x)
        loss = F.mse_loss(x_hat, x)

        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        """Validation step for PyTorch Lightning."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        x_hat = self(x)
        loss = F.mse_loss(x_hat, x)

        self.log("val_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        """Test step for PyTorch Lightning."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        x_hat = self(x)
        loss = F.mse_loss(x_hat, x)

        self.log("test_loss", loss, on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        """Configure optimizer for training."""
        optimizer = torch.optim.Adam(
            self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
        )
        return optimizer

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        """Prediction step for inference."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        return self(x)


class VariationalAutoEncoder(AutoEncoder):
    """
    A Variational Autoencoder (VAE) model extending the AutoEncoder class.

    This model includes reparameterization for stochastic sampling in the latent space.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        latent_dim: int,
        learning_rate: float = 1e-3,
        activation: str = "relu",
        dropout_rate: float = 0.0,
        weight_decay: float = 0.0,
        beta: float = 1.0,
    ):
        """
        Initialize the variational autoencoder.

        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions for encoder
            latent_dim: Dimension of the latent (bottleneck) layer
            learning_rate: Learning rate for optimization
            activation: Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu')
            dropout_rate: Dropout rate for regularization
            weight_decay: L2 regularization weight decay
            beta: Weight for KL divergence term in loss (beta-VAE)
        """
        # Initialize parent without building encoder/decoder
        super(AutoEncoder, self).__init__()
        self.save_hyperparameters()

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.weight_decay = weight_decay
        self.beta = beta

        # Get activation function
        self.activation_fn = self._get_activation_function(activation)

        # Build encoder (outputs mu and logvar)
        encoder_layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            encoder_layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation_fn,
                    nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                ]
            )
            prev_dim = hidden_dim

        self.encoder_backbone = nn.Sequential(*encoder_layers)

        # Separate layers for mean and log variance
        self.fc_mu = nn.Linear(prev_dim, latent_dim)
        self.fc_logvar = nn.Linear(prev_dim, latent_dim)

        # Build decoder
        decoder_layers = []
        prev_dim = latent_dim

        # Reverse the hidden dimensions for decoder
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation_fn,
                    nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                ]
            )
            prev_dim = hidden_dim

        # Add final reconstruction layer
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Encode input to latent distribution parameters (mu, logvar)."""
        h = self.encoder_backbone(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick for sampling from latent distribution."""
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        else:
            return mu

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to reconstruction."""
        return self.decoder(z)

    def forward(
        self, x: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass through VAE."""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstruction = self.decode(z)
        return reconstruction, mu, logvar

    def vae_loss(
        self,
        x: torch.Tensor,
        reconstruction: torch.Tensor,
        mu: torch.Tensor,
        logvar: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Compute VAE loss with reconstruction and KL divergence terms."""
        # Reconstruction loss
        recon_loss = F.mse_loss(reconstruction, x, reduction="sum")

        # KL divergence loss
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

        # Total loss
        total_loss = recon_loss + self.beta * kl_loss

        return total_loss, recon_loss, kl_loss

    def training_step(self, batch, batch_idx):
        """Training step for VAE."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        reconstruction, mu, logvar = self(x)

        total_loss, recon_loss, kl_loss = self.vae_loss(x, reconstruction, mu, logvar)

        # Normalize by batch size
        batch_size = x.size(0)
        total_loss = total_loss / batch_size
        recon_loss = recon_loss / batch_size
        kl_loss = kl_loss / batch_size

        self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log("train_recon_loss", recon_loss, on_step=True, on_epoch=True)
        self.log("train_kl_loss", kl_loss, on_step=True, on_epoch=True)

        return total_loss

    def validation_step(self, batch, batch_idx):
        """Validation step for VAE."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        reconstruction, mu, logvar = self(x)

        total_loss, recon_loss, kl_loss = self.vae_loss(x, reconstruction, mu, logvar)

        # Normalize by batch size
        batch_size = x.size(0)
        total_loss = total_loss / batch_size
        recon_loss = recon_loss / batch_size
        kl_loss = kl_loss / batch_size

        self.log("val_loss", total_loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log("val_recon_loss", recon_loss, on_step=False, on_epoch=True)
        self.log("val_kl_loss", kl_loss, on_step=False, on_epoch=True)

        return total_loss

    def test_step(self, batch, batch_idx):
        """Test step for VAE."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)
        reconstruction, mu, logvar = self(x)

        total_loss, recon_loss, kl_loss = self.vae_loss(x, reconstruction, mu, logvar)

        # Normalize by batch size
        batch_size = x.size(0)
        total_loss = total_loss / batch_size
        recon_loss = recon_loss / batch_size
        kl_loss = kl_loss / batch_size

        self.log("test_loss", total_loss, on_step=False, on_epoch=True)
        self.log("test_recon_loss", recon_loss, on_step=False, on_epoch=True)
        self.log("test_kl_loss", kl_loss, on_step=False, on_epoch=True)

        return total_loss

    def sample(
        self, num_samples: int, device: Optional[Union[str, torch.device]] = None
    ) -> torch.Tensor:
        """Generate samples from the latent space."""
        if device is None:
            device = next(self.parameters()).device

        with torch.no_grad():
            z = torch.randn(num_samples, self.latent_dim, device=device)
            samples = self.decode(z)

        return samples


class DenoisingAutoEncoder(AutoEncoder):
    """
    A Denoising Autoencoder (DAE) model extending the AutoEncoder class.

    This model adds noise to the input data during training for robustness.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        latent_dim: int,
        learning_rate: float = 1e-3,
        activation: str = "relu",
        dropout_rate: float = 0.0,
        weight_decay: float = 0.0,
        noise_factor: float = 0.1,
        noise_type: str = "gaussian",
    ):
        """
        Initialize the denoising autoencoder.

        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions for encoder
            latent_dim: Dimension of the latent (bottleneck) layer
            learning_rate: Learning rate for optimization
            activation: Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu')
            dropout_rate: Dropout rate for regularization
            weight_decay: L2 regularization weight decay
            noise_factor: Factor controlling the amount of noise added
            noise_type: Type of noise ('gaussian', 'uniform', 'masking')
        """
        super().__init__(
            input_dim=input_dim,
            hidden_dims=hidden_dims,
            latent_dim=latent_dim,
            learning_rate=learning_rate,
            activation=activation,
            dropout_rate=dropout_rate,
            weight_decay=weight_decay,
        )
        self.noise_factor = noise_factor
        self.noise_type = noise_type

    def add_noise(self, x: torch.Tensor) -> torch.Tensor:
        """Add noise to input data during training."""
        if not self.training:
            return x

        if self.noise_type == "gaussian":
            # Add Gaussian noise
            noise = torch.randn_like(x) * self.noise_factor
            return x + noise

        elif self.noise_type == "uniform":
            # Add uniform noise
            noise = (torch.rand_like(x) - 0.5) * 2 * self.noise_factor
            return x + noise

        elif self.noise_type == "masking":
            # Randomly mask (set to zero) some inputs
            mask = torch.rand_like(x) > self.noise_factor
            return x * mask.float()

        else:
            raise ValueError(f"Unsupported noise type: {self.noise_type}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through denoising autoencoder."""
        # Add noise to input during training
        noisy_x = self.add_noise(x)

        # Encode noisy input
        z = self.encode(noisy_x)

        # Decode to reconstruct original (clean) input
        reconstruction = self.decode(z)

        return reconstruction

    def training_step(self, batch, batch_idx):
        """Training step for denoising autoencoder."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)

        # Forward pass with noise injection
        x_hat = self(x)

        # Loss is between reconstruction and original clean input
        loss = F.mse_loss(x_hat, x)

        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        """Validation step for denoising autoencoder."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)

        # During validation, we can test both clean and noisy reconstruction
        x_hat_clean = super().forward(x)  # Clean reconstruction
        x_hat_noisy = self(x)  # Potentially noisy input reconstruction

        loss_clean = F.mse_loss(x_hat_clean, x)
        loss_noisy = F.mse_loss(x_hat_noisy, x)

        self.log("val_loss", loss_clean, on_step=False, on_epoch=True, prog_bar=True)
        self.log("val_loss_clean", loss_clean, on_step=False, on_epoch=True)
        self.log("val_loss_noisy", loss_noisy, on_step=False, on_epoch=True)

        return loss_clean

    def test_step(self, batch, batch_idx):
        """Test step for denoising autoencoder."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)

        # Test both clean and noisy reconstruction
        x_hat_clean = super().forward(x)  # Clean reconstruction
        x_hat_noisy = self(x)  # Potentially noisy input reconstruction

        loss_clean = F.mse_loss(x_hat_clean, x)
        loss_noisy = F.mse_loss(x_hat_noisy, x)

        self.log("test_loss", loss_clean, on_step=False, on_epoch=True)
        self.log("test_loss_clean", loss_clean, on_step=False, on_epoch=True)
        self.log("test_loss_noisy", loss_noisy, on_step=False, on_epoch=True)

        return loss_clean

    def denoise(self, x: torch.Tensor) -> torch.Tensor:
        """Denoise input data by passing through the autoencoder."""
        self.eval()
        with torch.no_grad():
            return super().forward(x)


class SparseAutoEncoder(AutoEncoder):
    """
    A Sparse Autoencoder model extending the AutoEncoder class.

    This model includes sparsity constraints on the latent representation.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        latent_dim: int,
        learning_rate: float = 1e-3,
        activation: str = "relu",
        dropout_rate: float = 0.0,
        weight_decay: float = 0.0,
        sparsity_weight: float = 1e-3,
        sparsity_target: float = 0.05,
        sparsity_type: str = "kl",
    ):
        """
        Initialize the sparse autoencoder.

        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions for encoder
            latent_dim: Dimension of the latent (bottleneck) layer
            learning_rate: Learning rate for optimization
            activation: Activation function ('relu', 'tanh', 'sigmoid', 'leaky_relu')
            dropout_rate: Dropout rate for regularization
            weight_decay: L2 regularization weight decay
            sparsity_weight: Weight for sparsity penalty in loss
            sparsity_target: Target average activation for sparsity
            sparsity_type: Type of sparsity penalty ('kl', 'l1', 'l2')
        """
        super().__init__(
            input_dim=input_dim,
            hidden_dims=hidden_dims,
            latent_dim=latent_dim,
            learning_rate=learning_rate,
            activation=activation,
            dropout_rate=dropout_rate,
            weight_decay=weight_decay,
        )
        self.sparsity_weight = sparsity_weight
        self.sparsity_target = sparsity_target
        self.sparsity_type = sparsity_type

    def compute_sparsity_penalty(
        self, latent_activations: torch.Tensor
    ) -> torch.Tensor:
        """Compute sparsity penalty for latent activations."""
        if self.sparsity_type == "l1":
            # L1 penalty encourages sparse activations
            return torch.mean(torch.abs(latent_activations))

        elif self.sparsity_type == "l2":
            # L2 penalty on activations
            return torch.mean(latent_activations**2)

        elif self.sparsity_type == "kl":
            # KL divergence penalty (commonly used in sparse autoencoders)
            # Average activation across batch
            rho_hat = torch.mean(torch.sigmoid(latent_activations), dim=0)
            rho = self.sparsity_target

            # KL divergence: KL(rho || rho_hat)
            kl_div = rho * torch.log(rho / (rho_hat + 1e-8)) + (1 - rho) * torch.log(
                (1 - rho) / (1 - rho_hat + 1e-8)
            )

            return torch.sum(kl_div)

        else:
            raise ValueError(f"Unsupported sparsity type: {self.sparsity_type}")

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through sparse autoencoder, returning reconstruction and latent."""
        latent = self.encode(x)
        reconstruction = self.decode(latent)
        return reconstruction, latent

    def training_step(self, batch, batch_idx):
        """Training step for sparse autoencoder."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)

        reconstruction, latent = self(x)

        # Reconstruction loss
        recon_loss = F.mse_loss(reconstruction, x)

        # Sparsity penalty
        sparsity_penalty = self.compute_sparsity_penalty(latent)

        # Total loss
        total_loss = recon_loss + self.sparsity_weight * sparsity_penalty

        self.log("train_loss", total_loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log("train_recon_loss", recon_loss, on_step=True, on_epoch=True)
        self.log(
            "train_sparsity_penalty", sparsity_penalty, on_step=True, on_epoch=True
        )

        # Log average activation (useful for monitoring sparsity)
        avg_activation = torch.mean(torch.abs(latent))
        self.log("train_avg_activation", avg_activation, on_step=True, on_epoch=True)

        return total_loss

    def validation_step(self, batch, batch_idx):
        """Validation step for sparse autoencoder."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)

        reconstruction, latent = self(x)

        # Reconstruction loss
        recon_loss = F.mse_loss(reconstruction, x)

        # Sparsity penalty
        sparsity_penalty = self.compute_sparsity_penalty(latent)

        # Total loss
        total_loss = recon_loss + self.sparsity_weight * sparsity_penalty

        self.log("val_loss", total_loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log("val_recon_loss", recon_loss, on_step=False, on_epoch=True)
        self.log("val_sparsity_penalty", sparsity_penalty, on_step=False, on_epoch=True)

        # Log average activation
        avg_activation = torch.mean(torch.abs(latent))
        self.log("val_avg_activation", avg_activation, on_step=False, on_epoch=True)

        return total_loss

    def test_step(self, batch, batch_idx):
        """Test step for sparse autoencoder."""
        x, *_ = batch if isinstance(batch, (list, tuple)) else (batch,)

        reconstruction, latent = self(x)

        # Reconstruction loss
        recon_loss = F.mse_loss(reconstruction, x)

        # Sparsity penalty
        sparsity_penalty = self.compute_sparsity_penalty(latent)

        # Total loss
        total_loss = recon_loss + self.sparsity_weight * sparsity_penalty

        self.log("test_loss", total_loss, on_step=False, on_epoch=True)
        self.log("test_recon_loss", recon_loss, on_step=False, on_epoch=True)
        self.log(
            "test_sparsity_penalty", sparsity_penalty, on_step=False, on_epoch=True
        )

        # Log average activation and sparsity metrics
        avg_activation = torch.mean(torch.abs(latent))
        sparsity_ratio = torch.mean(
            (torch.abs(latent) < 1e-3).float()
        )  # Fraction of near-zero activations

        self.log("test_avg_activation", avg_activation, on_step=False, on_epoch=True)
        self.log("test_sparsity_ratio", sparsity_ratio, on_step=False, on_epoch=True)

        return total_loss

    def get_sparse_features(
        self, x: torch.Tensor, threshold: float = 1e-3
    ) -> torch.Tensor:
        """Extract sparse features by thresholding latent activations."""
        self.eval()
        with torch.no_grad():
            latent = self.encode(x)
            # Apply threshold to create sparse representation
            sparse_latent = torch.where(
                torch.abs(latent) > threshold, latent, torch.zeros_like(latent)
            )
        return sparse_latent
