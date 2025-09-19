"""Tests for specialized autoencoder models."""

import numpy as np
import pytest
import torch

from encdr.autoencoder import (AutoEncoder, DenoisingAutoEncoder,
                               SparseAutoEncoder, VariationalAutoEncoder)


class TestVariationalAutoEncoder:
    """Test suite for VariationalAutoEncoder class."""

    def test_vae_initialization(self):
        """Test VAE initialization with default parameters."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)

        assert model.input_dim == 20
        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.learning_rate == 1e-3
        assert model.beta == 1.0
        assert hasattr(model, "encoder_backbone")
        assert hasattr(model, "fc_mu")
        assert hasattr(model, "fc_logvar")

    def test_vae_initialization_custom_params(self):
        """Test VAE initialization with custom parameters."""
        model = VariationalAutoEncoder(
            input_dim=50,
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
            beta=2.0,
        )

        assert model.input_dim == 50
        assert model.latent_dim == 10
        assert model.beta == 2.0
        assert model.learning_rate == 0.01

    def test_vae_encode_returns_mu_logvar(self):
        """Test that VAE encode returns both mu and logvar."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        x = torch.randn(10, 20)

        mu, logvar = model.encode(x)

        assert mu.shape == (10, 4)
        assert logvar.shape == (10, 4)
        assert isinstance(mu, torch.Tensor)
        assert isinstance(logvar, torch.Tensor)

    def test_vae_reparameterization(self):
        """Test reparameterization trick."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        mu = torch.randn(10, 4)
        logvar = torch.randn(10, 4)

        # Test training mode (stochastic)
        model.train()
        z1 = model.reparameterize(mu, logvar)
        z2 = model.reparameterize(mu, logvar)

        assert z1.shape == (10, 4)
        assert z2.shape == (10, 4)
        # Should be different due to randomness
        assert not torch.allclose(z1, z2, atol=1e-6)

        # Test eval mode (deterministic)
        model.eval()
        z3 = model.reparameterize(mu, logvar)
        z4 = model.reparameterize(mu, logvar)

        # Should return mu in eval mode
        assert torch.allclose(z3, mu, atol=1e-6)
        assert torch.allclose(z4, mu, atol=1e-6)

    def test_vae_forward_pass(self):
        """Test VAE forward pass returns reconstruction, mu, logvar."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        x = torch.randn(10, 20)

        reconstruction, mu, logvar = model(x)

        assert reconstruction.shape == (10, 20)
        assert mu.shape == (10, 4)
        assert logvar.shape == (10, 4)

    def test_vae_loss_computation(self):
        """Test VAE loss computation."""
        model = VariationalAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, beta=1.0
        )
        x = torch.randn(10, 20)
        reconstruction, mu, logvar = model(x)

        total_loss, recon_loss, kl_loss = model.vae_loss(x, reconstruction, mu, logvar)

        assert isinstance(total_loss, torch.Tensor)
        assert isinstance(recon_loss, torch.Tensor)
        assert isinstance(kl_loss, torch.Tensor)
        assert total_loss.item() >= 0
        assert recon_loss.item() >= 0
        assert kl_loss.item() >= 0

    def test_vae_beta_weighting(self):
        """Test that beta parameter affects KL divergence weighting."""
        x = torch.randn(10, 20)

        # Create models with same initialization
        torch.manual_seed(42)
        model1 = VariationalAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, beta=1.0
        )

        torch.manual_seed(42)
        model2 = VariationalAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, beta=2.0
        )

        # Set to eval mode to make reparameterization deterministic
        model1.eval()
        model2.eval()

        reconstruction1, mu1, logvar1 = model1(x)
        total_loss1, recon_loss1, kl_loss1 = model1.vae_loss(
            x, reconstruction1, mu1, logvar1
        )

        reconstruction2, mu2, logvar2 = model2(x)
        total_loss2, recon_loss2, kl_loss2 = model2.vae_loss(
            x, reconstruction2, mu2, logvar2
        )

        # With same initialization and eval mode, reconstructions should be very similar
        # KL loss should be the same, but total loss should be different due to beta
        assert torch.allclose(kl_loss1, kl_loss2, atol=1e-3)
        assert torch.allclose(recon_loss1, recon_loss2, atol=1e-3)
        # Total loss with beta=2.0 should be higher (more KL penalty)
        assert total_loss2.item() > total_loss1.item()

    def test_vae_training_step(self):
        """Test VAE training step."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.training_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_vae_validation_step(self):
        """Test VAE validation step."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.validation_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_vae_test_step(self):
        """Test VAE test step."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.test_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_vae_sampling(self):
        """Test VAE sampling from latent space."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)

        # Test sampling
        samples = model.sample(5)
        assert samples.shape == (5, 20)

        # Test sampling with specific device
        if torch.cuda.is_available():
            model = model.cuda()
            samples_cuda = model.sample(3, device="cuda")
            assert samples_cuda.shape == (3, 20)
            assert samples_cuda.device.type == "cuda"

    def test_vae_decode_functionality(self):
        """Test VAE decode functionality."""
        model = VariationalAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        z = torch.randn(10, 4)

        decoded = model.decode(z)
        assert decoded.shape == (10, 20)

    def test_vae_batch_handling_with_tuples(self):
        """Test VAE handling of batch data as tuples."""
        model = VariationalAutoEncoder(input_dim=10, hidden_dims=[8], latent_dim=4)

        # Test with tuple batch (x, y)
        x = torch.randn(16, 10)
        y = torch.randn(16, 1)
        batch = (x, y)

        loss = model.training_step(batch, 0)
        assert isinstance(loss, torch.Tensor)

        # Test with single tensor batch
        batch = x
        loss = model.training_step(batch, 0)
        assert isinstance(loss, torch.Tensor)


class TestDenoisingAutoEncoder:
    """Test suite for DenoisingAutoEncoder class."""

    def test_dae_initialization(self):
        """Test DAE initialization with default parameters."""
        model = DenoisingAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)

        assert model.input_dim == 20
        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.noise_factor == 0.1
        assert model.noise_type == "gaussian"

    def test_dae_initialization_custom_params(self):
        """Test DAE initialization with custom parameters."""
        model = DenoisingAutoEncoder(
            input_dim=50,
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
            noise_factor=0.2,
            noise_type="uniform",
        )

        assert model.input_dim == 50
        assert model.latent_dim == 10
        assert model.noise_factor == 0.2
        assert model.noise_type == "uniform"

    def test_dae_gaussian_noise(self):
        """Test Gaussian noise addition."""
        model = DenoisingAutoEncoder(
            input_dim=20,
            hidden_dims=[16, 8],
            latent_dim=4,
            noise_factor=0.1,
            noise_type="gaussian",
        )
        x = torch.randn(10, 20)

        # Training mode - should add noise
        model.train()
        noisy_x1 = model.add_noise(x)
        noisy_x2 = model.add_noise(x)

        assert noisy_x1.shape == x.shape
        assert not torch.allclose(noisy_x1, x, atol=1e-6)
        assert not torch.allclose(noisy_x1, noisy_x2, atol=1e-6)

        # Eval mode - should not add noise
        model.eval()
        clean_x = model.add_noise(x)
        assert torch.allclose(clean_x, x, atol=1e-6)

    def test_dae_uniform_noise(self):
        """Test uniform noise addition."""
        model = DenoisingAutoEncoder(
            input_dim=20,
            hidden_dims=[16, 8],
            latent_dim=4,
            noise_factor=0.1,
            noise_type="uniform",
        )
        x = torch.randn(10, 20)

        model.train()
        noisy_x = model.add_noise(x)

        assert noisy_x.shape == x.shape
        assert not torch.allclose(noisy_x, x, atol=1e-6)

    def test_dae_masking_noise(self):
        """Test masking noise addition."""
        model = DenoisingAutoEncoder(
            input_dim=20,
            hidden_dims=[16, 8],
            latent_dim=4,
            noise_factor=0.3,
            noise_type="masking",
        )
        x = torch.ones(10, 20)  # Use ones to easily see masking effect

        model.train()
        masked_x = model.add_noise(x)

        assert masked_x.shape == x.shape
        # Some values should be masked (set to 0)
        assert (masked_x == 0).sum() > 0
        # Remaining values should be 1
        assert torch.all((masked_x == 0) | (masked_x == 1))

    def test_dae_invalid_noise_type(self):
        """Test that invalid noise type raises error."""
        model = DenoisingAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, noise_type="invalid"
        )
        x = torch.randn(10, 20)

        model.train()
        with pytest.raises(ValueError, match="Unsupported noise type"):
            model.add_noise(x)

    def test_dae_forward_pass(self):
        """Test DAE forward pass with noise injection."""
        model = DenoisingAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, noise_factor=0.1
        )
        x = torch.randn(10, 20)

        # Training mode
        model.train()
        reconstruction = model(x)
        assert reconstruction.shape == x.shape

        # Eval mode
        model.eval()
        reconstruction_eval = model(x)
        assert reconstruction_eval.shape == x.shape

    def test_dae_training_step(self):
        """Test DAE training step."""
        model = DenoisingAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.training_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_dae_validation_step(self):
        """Test DAE validation step."""
        model = DenoisingAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.validation_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_dae_test_step(self):
        """Test DAE test step."""
        model = DenoisingAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.test_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_dae_denoise_method(self):
        """Test DAE denoise method."""
        model = DenoisingAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        x = torch.randn(10, 20)

        denoised = model.denoise(x)

        assert denoised.shape == x.shape
        assert isinstance(denoised, torch.Tensor)


class TestSparseAutoEncoder:
    """Test suite for SparseAutoEncoder class."""

    def test_sae_initialization(self):
        """Test SAE initialization with default parameters."""
        model = SparseAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)

        assert model.input_dim == 20
        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.sparsity_weight == 1e-3
        assert model.sparsity_target == 0.05
        assert model.sparsity_type == "kl"

    def test_sae_initialization_custom_params(self):
        """Test SAE initialization with custom parameters."""
        model = SparseAutoEncoder(
            input_dim=50,
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
            sparsity_weight=1e-2,
            sparsity_target=0.1,
            sparsity_type="l1",
        )

        assert model.input_dim == 50
        assert model.latent_dim == 10
        assert model.sparsity_weight == 1e-2
        assert model.sparsity_target == 0.1
        assert model.sparsity_type == "l1"

    def test_sae_l1_sparsity_penalty(self):
        """Test L1 sparsity penalty computation."""
        model = SparseAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, sparsity_type="l1"
        )
        latent = torch.randn(10, 4)

        penalty = model.compute_sparsity_penalty(latent)

        assert isinstance(penalty, torch.Tensor)
        assert penalty.item() >= 0
        expected_penalty = torch.mean(torch.abs(latent))
        assert torch.allclose(penalty, expected_penalty, atol=1e-6)

    def test_sae_l2_sparsity_penalty(self):
        """Test L2 sparsity penalty computation."""
        model = SparseAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, sparsity_type="l2"
        )
        latent = torch.randn(10, 4)

        penalty = model.compute_sparsity_penalty(latent)

        assert isinstance(penalty, torch.Tensor)
        assert penalty.item() >= 0
        expected_penalty = torch.mean(latent**2)
        assert torch.allclose(penalty, expected_penalty, atol=1e-6)

    def test_sae_kl_sparsity_penalty(self):
        """Test KL divergence sparsity penalty computation."""
        model = SparseAutoEncoder(
            input_dim=20,
            hidden_dims=[16, 8],
            latent_dim=4,
            sparsity_type="kl",
            sparsity_target=0.05,
        )
        latent = torch.randn(10, 4)

        penalty = model.compute_sparsity_penalty(latent)

        assert isinstance(penalty, torch.Tensor)
        assert penalty.item() >= 0

    def test_sae_invalid_sparsity_type(self):
        """Test that invalid sparsity type raises error."""
        model = SparseAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, sparsity_type="invalid"
        )
        latent = torch.randn(10, 4)

        with pytest.raises(ValueError, match="Unsupported sparsity type"):
            model.compute_sparsity_penalty(latent)

    def test_sae_forward_pass(self):
        """Test SAE forward pass returns reconstruction and latent."""
        model = SparseAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        x = torch.randn(10, 20)

        reconstruction, latent = model(x)

        assert reconstruction.shape == (10, 20)
        assert latent.shape == (10, 4)

    def test_sae_training_step(self):
        """Test SAE training step includes sparsity penalty."""
        model = SparseAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.training_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_sae_validation_step(self):
        """Test SAE validation step."""
        model = SparseAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.validation_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_sae_test_step(self):
        """Test SAE test step."""
        model = SparseAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        batch = torch.randn(16, 20)

        loss = model.test_step(batch, 0)

        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0

    def test_sae_get_sparse_features(self):
        """Test sparse feature extraction with thresholding."""
        model = SparseAutoEncoder(input_dim=20, hidden_dims=[16, 8], latent_dim=4)
        x = torch.randn(10, 20)

        sparse_features = model.get_sparse_features(x, threshold=0.1)

        assert sparse_features.shape == (10, 4)
        # Check that small values are set to zero
        assert torch.all((torch.abs(sparse_features) >= 0.1) | (sparse_features == 0))

    def test_sae_sparsity_effect(self):
        """Test that sparsity weight affects loss computation."""
        x = torch.randn(10, 20)

        # Model with low sparsity weight
        model1 = SparseAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, sparsity_weight=1e-5
        )
        reconstruction1, latent1 = model1(x)
        recon_loss1 = torch.nn.functional.mse_loss(reconstruction1, x)
        sparsity_penalty1 = model1.compute_sparsity_penalty(latent1)
        total_loss1 = recon_loss1 + model1.sparsity_weight * sparsity_penalty1

        # Model with high sparsity weight
        model2 = SparseAutoEncoder(
            input_dim=20, hidden_dims=[16, 8], latent_dim=4, sparsity_weight=1e-1
        )
        model2.load_state_dict(model1.state_dict())  # Same weights for fair comparison
        reconstruction2, latent2 = model2(x)
        recon_loss2 = torch.nn.functional.mse_loss(reconstruction2, x)
        sparsity_penalty2 = model2.compute_sparsity_penalty(latent2)
        total_loss2 = recon_loss2 + model2.sparsity_weight * sparsity_penalty2

        # Reconstruction loss should be the same, sparsity penalty should be the same,
        # but total loss should be different due to different weighting
        assert torch.allclose(recon_loss1, recon_loss2, atol=1e-6)
        assert torch.allclose(sparsity_penalty1, sparsity_penalty2, atol=1e-6)
        assert total_loss2.item() > total_loss1.item()
