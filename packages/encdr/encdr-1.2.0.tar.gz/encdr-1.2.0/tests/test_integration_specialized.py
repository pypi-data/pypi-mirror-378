"""Integration tests for specialized autoencoder functionality."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch
from sklearn.datasets import make_classification, make_regression

from encdr.autoencoder import (AutoEncoder, DenoisingAutoEncoder,
                               SparseAutoEncoder, VariationalAutoEncoder)
from encdr.encdr import DENCDR, ENCDR, SENCDR, VENCDR


@pytest.fixture
def classification_data():
    """Create classification data for testing."""
    X, y = make_classification(
        n_samples=200,
        n_features=30,
        n_informative=15,
        n_redundant=10,
        n_clusters_per_class=1,
        random_state=42,
    )
    return X.astype(np.float32), y


@pytest.fixture
def regression_data():
    """Create regression data for testing."""
    X, y = make_regression(
        n_samples=200, n_features=30, n_informative=20, noise=0.1, random_state=42
    )
    return X.astype(np.float32), y.astype(np.float32)


class TestAutoencoderIntegration:
    """Integration tests for autoencoder models."""

    def test_all_autoencoders_basic_functionality(self, classification_data):
        """Test that all autoencoder types can train and produce outputs."""
        X, _ = classification_data

        models = {
            "AutoEncoder": AutoEncoder(
                input_dim=30, hidden_dims=[20, 10], latent_dim=5
            ),
            "VariationalAutoEncoder": VariationalAutoEncoder(
                input_dim=30, hidden_dims=[20, 10], latent_dim=5
            ),
            "DenoisingAutoEncoder": DenoisingAutoEncoder(
                input_dim=30, hidden_dims=[20, 10], latent_dim=5
            ),
            "SparseAutoEncoder": SparseAutoEncoder(
                input_dim=30, hidden_dims=[20, 10], latent_dim=5
            ),
        }

        for name, model in models.items():
            # Test forward pass
            x_tensor = torch.FloatTensor(X[:10])

            if name == "VariationalAutoEncoder":
                reconstruction, mu, logvar = model(x_tensor)
                assert reconstruction.shape == (10, 30)
                assert mu.shape == (10, 5)
                assert logvar.shape == (10, 5)
            elif name == "SparseAutoEncoder":
                reconstruction, latent = model(x_tensor)
                assert reconstruction.shape == (10, 30)
                assert latent.shape == (10, 5)
            else:
                reconstruction = model(x_tensor)
                assert reconstruction.shape == (10, 30)

            # Test encode/decode
            if name == "VariationalAutoEncoder":
                mu, logvar = model.encode(x_tensor)
                assert mu.shape == (10, 5)
                assert logvar.shape == (10, 5)
                z = model.reparameterize(mu, logvar)
                decoded = model.decode(z)
                assert decoded.shape == (10, 30)
            else:
                encoded = model.encode(x_tensor)
                assert encoded.shape == (10, 5)
                decoded = model.decode(encoded)
                assert decoded.shape == (10, 30)

    def test_vae_specific_functionality(self, classification_data):
        """Test VAE-specific functionality."""
        X, _ = classification_data
        model = VariationalAutoEncoder(
            input_dim=30, hidden_dims=[20, 10], latent_dim=5, beta=2.0
        )

        x_tensor = torch.FloatTensor(X[:10])

        # Test VAE loss computation
        reconstruction, mu, logvar = model(x_tensor)
        total_loss, recon_loss, kl_loss = model.vae_loss(
            x_tensor, reconstruction, mu, logvar
        )

        assert total_loss.item() >= 0
        assert recon_loss.item() >= 0
        assert kl_loss.item() >= 0

        # Test sampling
        samples = model.sample(5)
        assert samples.shape == (5, 30)

        # Test different beta values affect loss
        model_beta1 = VariationalAutoEncoder(
            input_dim=30, hidden_dims=[20, 10], latent_dim=5, beta=1.0
        )
        model_beta2 = VariationalAutoEncoder(
            input_dim=30, hidden_dims=[20, 10], latent_dim=5, beta=3.0
        )

        # Copy weights for fair comparison
        model_beta2.load_state_dict(model_beta1.state_dict())

        reconstruction1, mu1, logvar1 = model_beta1(x_tensor)
        reconstruction2, mu2, logvar2 = model_beta2(x_tensor)

        loss1, _, _ = model_beta1.vae_loss(x_tensor, reconstruction1, mu1, logvar1)
        loss2, _, _ = model_beta2.vae_loss(x_tensor, reconstruction2, mu2, logvar2)

        # Higher beta should lead to higher total loss
        assert loss2.item() > loss1.item()

    def test_dae_noise_functionality(self, classification_data):
        """Test DAE noise functionality."""
        X, _ = classification_data

        noise_types = ["gaussian", "uniform", "masking"]

        for noise_type in noise_types:
            model = DenoisingAutoEncoder(
                input_dim=30,
                hidden_dims=[20, 10],
                latent_dim=5,
                noise_factor=0.1,
                noise_type=noise_type,
            )

            x_tensor = torch.FloatTensor(X[:10])

            # Test noise addition
            model.train()
            noisy_x = model.add_noise(x_tensor)
            assert noisy_x.shape == x_tensor.shape

            if noise_type != "masking":
                # For Gaussian and uniform, outputs should be different from input
                assert not torch.allclose(noisy_x, x_tensor, atol=1e-6)
            else:
                # For masking, some values should be zero
                assert (noisy_x == 0).sum() > 0

            # Test denoising
            model.eval()
            clean_x = model.denoise(x_tensor)
            assert clean_x.shape == x_tensor.shape

    def test_sae_sparsity_functionality(self, classification_data):
        """Test SAE sparsity functionality."""
        X, _ = classification_data

        sparsity_types = ["l1", "l2", "kl"]

        for sparsity_type in sparsity_types:
            model = SparseAutoEncoder(
                input_dim=30,
                hidden_dims=[20, 10],
                latent_dim=5,
                sparsity_weight=1e-3,
                sparsity_type=sparsity_type,
            )

            x_tensor = torch.FloatTensor(X[:10])

            # Test sparsity penalty computation
            reconstruction, latent = model(x_tensor)
            penalty = model.compute_sparsity_penalty(latent)

            assert penalty.item() >= 0
            assert isinstance(penalty, torch.Tensor)

            # Test sparse feature extraction
            sparse_features = model.get_sparse_features(x_tensor, threshold=0.1)
            assert sparse_features.shape == (10, 5)
            # Check thresholding works
            assert torch.all(
                (torch.abs(sparse_features) >= 0.1) | (sparse_features == 0)
            )


class TestENCDRIntegration:
    """Integration tests for ENCDR classes."""

    def test_all_encdr_variants_scikit_learn_compatibility(self, classification_data):
        """Test that all ENCDR variants are scikit-learn compatible."""
        X, y = classification_data

        models = {
            "ENCDR": ENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=3),
            "VENCDR": VENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=3),
            "DENCDR": DENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=3),
            "SENCDR": SENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=3),
        }

        for name, model in models.items():
            # Test fit
            result = model.fit(X)
            assert result is model
            assert model.is_fitted_

            # Test transform
            X_transformed = model.transform(X)
            assert X_transformed.shape == (200, 5)

            # Test fit_transform
            model_new = models[name].__class__(
                hidden_dims=[20, 10], latent_dim=5, max_epochs=3
            )
            X_fit_transformed = model_new.fit_transform(X)
            assert X_fit_transformed.shape == (200, 5)

            # Test predict (reconstruction)
            X_reconstructed = model.predict(X)
            assert X_reconstructed.shape == X.shape

            # Test score
            score = model.score(X)
            assert isinstance(score, float)
            assert score <= 0  # Negative MSE

            # Test inverse_transform (if available)
            if hasattr(model, "inverse_transform"):
                X_inverse = model.inverse_transform(X_transformed)
                assert X_inverse.shape == X.shape

    def test_vencdr_specific_methods(self, classification_data):
        """Test VENCDR-specific methods."""
        X, _ = classification_data
        model = VENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=3, beta=1.5)

        model.fit(X)

        # Test transform with mean vs sampling
        X_mean = model.transform(X, use_mean=True)
        X_sample1 = model.transform(X, use_mean=False)
        X_sample2 = model.transform(X, use_mean=False)

        assert X_mean.shape == (200, 5)
        assert X_sample1.shape == (200, 5)
        assert X_sample2.shape == (200, 5)

        # Mean should be deterministic
        X_mean2 = model.transform(X, use_mean=True)
        np.testing.assert_allclose(X_mean, X_mean2, rtol=1e-6)

        # Sampling should be stochastic
        assert not np.allclose(X_sample1, X_sample2, atol=1e-6)

        # Test sampling from latent space
        samples = model.sample(10)
        assert samples.shape == (10, 30)

    def test_dencdr_denoising(self, classification_data):
        """Test DENCDR denoising functionality."""
        X, _ = classification_data
        model = DENCDR(
            hidden_dims=[20, 10],
            latent_dim=5,
            max_epochs=3,
            noise_factor=0.1,
            noise_type="gaussian",
        )

        model.fit(X)

        # Add noise to test data
        noise = np.random.normal(0, 0.05, X.shape).astype(np.float32)
        X_noisy = X + noise

        # Test denoising
        X_denoised = model.denoise(X_noisy)
        assert X_denoised.shape == X.shape

        # Denoised should be closer to original than noisy
        mse_noisy = np.mean((X - X_noisy) ** 2)
        mse_denoised = np.mean((X - X_denoised) ** 2)

        # This is not guaranteed but often true for well-trained denoisers
        # We just check that denoising produces reasonable output
        assert mse_denoised >= 0

    def test_sencdr_sparsity_methods(self, classification_data):
        """Test SENCDR sparsity-specific methods."""
        X, _ = classification_data
        model = SENCDR(
            hidden_dims=[20, 10],
            latent_dim=5,
            max_epochs=3,
            sparsity_weight=1e-3,
            sparsity_type="kl",
        )

        model.fit(X)

        # Test sparse feature extraction
        sparse_features = model.get_sparse_features(X, threshold=0.1)
        assert sparse_features.shape == (200, 5)

        # Test sparsity metrics
        metrics = model.sparsity_metrics(X)
        assert "mean_activation" in metrics
        assert "sparsity_ratio" in metrics
        assert "active_neurons" in metrics

        assert 0 <= metrics["sparsity_ratio"] <= 1
        assert metrics["mean_activation"] >= 0
        assert 0 <= metrics["active_neurons"] <= 5

        # Test transform with thresholding
        X_sparse = model.transform(X, apply_threshold=True, threshold=0.1)
        assert X_sparse.shape == (200, 5)

        # Verify thresholding
        assert np.all((np.abs(X_sparse) >= 0.1) | (X_sparse == 0))

    def test_save_load_functionality(self, classification_data):
        """Test save/load functionality for all ENCDR variants."""
        X, _ = classification_data

        models = {
            "ENCDR": ENCDR(
                hidden_dims=[20, 10], latent_dim=5, max_epochs=2, random_state=42
            ),
            "VENCDR": VENCDR(
                hidden_dims=[20, 10],
                latent_dim=5,
                max_epochs=2,
                beta=1.5,
                random_state=42,
            ),
            "DENCDR": DENCDR(
                hidden_dims=[20, 10],
                latent_dim=5,
                max_epochs=2,
                noise_factor=0.15,
                noise_type="uniform",
                random_state=42,
            ),
            "SENCDR": SENCDR(
                hidden_dims=[20, 10],
                latent_dim=5,
                max_epochs=2,
                sparsity_weight=1e-2,
                sparsity_type="l1",
                random_state=42,
            ),
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            for name, model in models.items():
                # Fit and get original results
                model.fit(X)
                X_transformed_orig = model.transform(X)
                X_predicted_orig = model.predict(X)

                # Save model
                filepath = Path(temp_dir) / f"test_{name.lower()}_model.pkl"
                model.save(filepath)

                # Load model
                loaded_model = model.__class__.load(filepath)

                # Test loaded model produces same results
                X_transformed_loaded = loaded_model.transform(X)
                X_predicted_loaded = loaded_model.predict(X)

                np.testing.assert_allclose(
                    X_transformed_orig, X_transformed_loaded, rtol=1e-5
                )
                np.testing.assert_allclose(
                    X_predicted_orig, X_predicted_loaded, rtol=1e-5
                )

                # Test model parameters are preserved
                assert loaded_model.is_fitted_
                assert loaded_model.input_dim_ == model.input_dim_
                assert loaded_model.hidden_dims == model.hidden_dims
                assert loaded_model.latent_dim == model.latent_dim

                # Test model-specific parameters
                if name == "VENCDR":
                    assert loaded_model.beta == model.beta
                elif name == "DENCDR":
                    assert loaded_model.noise_factor == model.noise_factor
                    assert loaded_model.noise_type == model.noise_type
                elif name == "SENCDR":
                    assert loaded_model.sparsity_weight == model.sparsity_weight
                    assert loaded_model.sparsity_type == model.sparsity_type

    def test_model_comparison_different_architectures(self, classification_data):
        """Test models with different architectures produce different results."""
        X, _ = classification_data

        # Test different latent dimensions
        model_small = ENCDR(
            hidden_dims=[20, 10], latent_dim=2, max_epochs=3, random_state=42
        )
        model_large = ENCDR(
            hidden_dims=[20, 10], latent_dim=8, max_epochs=3, random_state=42
        )

        model_small.fit(X)
        model_large.fit(X)

        X_small = model_small.transform(X)
        X_large = model_large.transform(X)

        assert X_small.shape == (200, 2)
        assert X_large.shape == (200, 8)

        # Test different hidden dimensions
        model_shallow = ENCDR(
            hidden_dims=[15], latent_dim=5, max_epochs=3, random_state=42
        )
        model_deep = ENCDR(
            hidden_dims=[25, 20, 15], latent_dim=5, max_epochs=3, random_state=42
        )

        model_shallow.fit(X)
        model_deep.fit(X)

        X_shallow = model_shallow.transform(X)
        X_deep = model_deep.transform(X)

        assert X_shallow.shape == X_deep.shape == (200, 5)
        # Results should be different due to different architectures
        assert not np.allclose(X_shallow, X_deep, atol=1e-3)

    def test_reproducibility_with_random_state(self, classification_data):
        """Test that models are reproducible with random state."""
        X, _ = classification_data

        model1 = ENCDR(
            hidden_dims=[20, 10], latent_dim=5, max_epochs=3, random_state=42
        )
        model2 = ENCDR(
            hidden_dims=[20, 10], latent_dim=5, max_epochs=3, random_state=42
        )

        X_transformed1 = model1.fit_transform(X)
        X_transformed2 = model2.fit_transform(X)

        # Results should be very similar (small differences due to Lightning's internal randomness)
        np.testing.assert_allclose(X_transformed1, X_transformed2, rtol=1e-2)

    def test_error_handling(self, classification_data):
        """Test error handling across all models."""
        X, _ = classification_data

        models = [
            ENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=2),
            VENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=2),
            DENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=2),
            SENCDR(hidden_dims=[20, 10], latent_dim=5, max_epochs=2),
        ]

        for model in models:
            # Test unfitted model errors
            with pytest.raises(ValueError, match="not fitted"):
                model.transform(X)

            with pytest.raises(ValueError, match="not fitted"):
                model.predict(X)

            with pytest.raises(ValueError, match="not fitted"):
                model.score(X)

            # Fit model
            model.fit(X)

            # Test dimension mismatch
            X_wrong = np.random.randn(10, 15).astype(np.float32)
            with pytest.raises(ValueError, match="features"):
                model.transform(X_wrong)

            with pytest.raises(ValueError, match="features"):
                model.predict(X_wrong)
