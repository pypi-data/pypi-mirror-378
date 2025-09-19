"""Tests for specialized ENCDR classes."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

from encdr.encdr import DENCDR, ENCDR, SENCDR, VENCDR


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    X, y = make_classification(
        n_samples=100,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        n_clusters_per_class=1,
        random_state=42,
    )
    return X.astype(np.float32), y


class TestVENCDR:
    """Test suite for VENCDR class."""

    def test_vencdr_initialization(self):
        """Test VENCDR initialization with default parameters."""
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4)

        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.beta == 1.0
        assert model.learning_rate == 1e-3
        assert not model.is_fitted_

    def test_vencdr_initialization_custom_params(self):
        """Test VENCDR initialization with custom parameters."""
        model = VENCDR(
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
            batch_size=64,
            max_epochs=50,
            validation_split=0.1,
            standardize=False,
            random_state=42,
            beta=2.0,
        )

        assert model.hidden_dims == [64, 32, 16]
        assert model.latent_dim == 10
        assert model.beta == 2.0
        assert model.learning_rate == 0.01
        assert model.batch_size == 64
        assert model.max_epochs == 50
        assert model.validation_split == 0.1
        assert model.standardize == False
        assert model.random_state == 42

    def test_vencdr_fit(self, sample_data):
        """Test VENCDR fitting."""
        X, _ = sample_data
        model = VENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            validation_split=0.2,
            random_state=42,
        )

        result = model.fit(X)

        assert result is model  # Should return self
        assert model.is_fitted_
        assert model.input_dim_ == 20
        assert model.model_ is not None
        assert model.scaler_ is not None

    def test_vencdr_fit_no_standardization(self, sample_data):
        """Test VENCDR fitting without standardization."""
        X, _ = sample_data
        model = VENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            standardize=False,
            random_state=42,
        )

        model.fit(X)

        assert model.is_fitted_
        assert model.scaler_ is None

    def test_vencdr_transform_mean(self, sample_data):
        """Test VENCDR transform using mean."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_transformed = model.transform(X, use_mean=True)

        assert X_transformed.shape == (100, 4)
        assert isinstance(X_transformed, np.ndarray)

    def test_vencdr_transform_sample(self, sample_data):
        """Test VENCDR transform using sampling."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_transformed1 = model.transform(X, use_mean=False)
        X_transformed2 = model.transform(X, use_mean=False)

        assert X_transformed1.shape == (100, 4)
        assert X_transformed2.shape == (100, 4)
        # Stochastic sampling should give different results
        assert not np.allclose(X_transformed1, X_transformed2, atol=1e-6)

    def test_vencdr_fit_transform(self, sample_data):
        """Test VENCDR fit_transform."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        X_transformed = model.fit_transform(X)

        assert X_transformed.shape == (100, 4)
        assert model.is_fitted_

    def test_vencdr_predict(self, sample_data):
        """Test VENCDR prediction (reconstruction)."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_reconstructed = model.predict(X)

        assert X_reconstructed.shape == X.shape
        assert isinstance(X_reconstructed, np.ndarray)

    def test_vencdr_sample(self, sample_data):
        """Test VENCDR sampling from latent space."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        samples = model.sample(5)

        assert samples.shape == (5, 20)
        assert isinstance(samples, np.ndarray)

    def test_vencdr_score(self, sample_data):
        """Test VENCDR scoring."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        score = model.score(X)

        assert isinstance(score, float)
        assert score <= 0  # Negative MSE

    def test_vencdr_errors_unfitted(self, sample_data):
        """Test VENCDR errors when not fitted."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4)

        with pytest.raises(ValueError, match="not fitted"):
            model.transform(X)

        with pytest.raises(ValueError, match="not fitted"):
            model.predict(X)

        with pytest.raises(ValueError, match="not fitted"):
            model.sample(5)

        with pytest.raises(ValueError, match="not fitted"):
            model.score(X)

    def test_vencdr_dimension_mismatch(self, sample_data):
        """Test VENCDR with dimension mismatch."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)

        # Wrong input dimension
        X_wrong = np.random.randn(10, 15).astype(np.float32)
        with pytest.raises(ValueError, match="features"):
            model.transform(X_wrong)

        with pytest.raises(ValueError, match="features"):
            model.predict(X_wrong)

    def test_vencdr_save_load(self, sample_data):
        """Test VENCDR save and load functionality."""
        X, _ = sample_data
        model = VENCDR(
            hidden_dims=[16, 8], latent_dim=4, max_epochs=2, beta=1.5, random_state=42
        )

        model.fit(X)
        X_transformed_orig = model.transform(X)

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_vencdr_model.pkl"
            model.save(filepath)

            # Load model
            loaded_model = VENCDR.load(filepath)

            assert loaded_model.is_fitted_
            assert loaded_model.input_dim_ == model.input_dim_
            assert loaded_model.beta == model.beta
            assert loaded_model.hidden_dims == model.hidden_dims

            # Test that loaded model produces same results
            X_transformed_loaded = loaded_model.transform(X)
            np.testing.assert_allclose(
                X_transformed_orig, X_transformed_loaded, rtol=1e-5
            )

    def test_vencdr_save_unfitted_error(self):
        """Test VENCDR save error when not fitted."""
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4)

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_model.pkl"
            with pytest.raises(ValueError, match="Cannot save an unfitted model"):
                model.save(filepath)


class TestDENCDR:
    """Test suite for DENCDR class."""

    def test_dencdr_initialization(self):
        """Test DENCDR initialization with default parameters."""
        model = DENCDR(hidden_dims=[16, 8], latent_dim=4)

        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.noise_factor == 0.1
        assert model.noise_type == "gaussian"
        assert not model.is_fitted_

    def test_dencdr_initialization_custom_params(self):
        """Test DENCDR initialization with custom parameters."""
        model = DENCDR(
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
            batch_size=64,
            max_epochs=50,
            validation_split=0.1,
            standardize=False,
            random_state=42,
            noise_factor=0.2,
            noise_type="uniform",
        )

        assert model.hidden_dims == [64, 32, 16]
        assert model.latent_dim == 10
        assert model.noise_factor == 0.2
        assert model.noise_type == "uniform"

    def test_dencdr_fit(self, sample_data):
        """Test DENCDR fitting."""
        X, _ = sample_data
        model = DENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            validation_split=0.2,
            random_state=42,
        )

        result = model.fit(X)

        assert result is model  # Should return self
        assert model.is_fitted_
        assert model.input_dim_ == 20
        assert model.model_ is not None
        assert model.scaler_ is not None

    def test_dencdr_transform(self, sample_data):
        """Test DENCDR transform."""
        X, _ = sample_data
        model = DENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_transformed = model.transform(X)

        assert X_transformed.shape == (100, 4)
        assert isinstance(X_transformed, np.ndarray)

    def test_dencdr_predict(self, sample_data):
        """Test DENCDR prediction (reconstruction)."""
        X, _ = sample_data
        model = DENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_reconstructed = model.predict(X)

        assert X_reconstructed.shape == X.shape
        assert isinstance(X_reconstructed, np.ndarray)

    def test_dencdr_denoise(self, sample_data):
        """Test DENCDR denoising functionality."""
        X, _ = sample_data
        model = DENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            noise_factor=0.1,
            random_state=42,
        )

        model.fit(X)

        # Add noise to data
        noise = np.random.normal(0, 0.1, X.shape).astype(np.float32)
        X_noisy = X + noise

        X_denoised = model.denoise(X_noisy)

        assert X_denoised.shape == X.shape
        assert isinstance(X_denoised, np.ndarray)

    def test_dencdr_save_load(self, sample_data):
        """Test DENCDR save and load functionality."""
        X, _ = sample_data
        model = DENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            noise_factor=0.15,
            noise_type="uniform",
            random_state=42,
        )

        model.fit(X)
        X_transformed_orig = model.transform(X)

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_dencdr_model.pkl"
            model.save(filepath)

            # Load model
            loaded_model = DENCDR.load(filepath)

            assert loaded_model.is_fitted_
            assert loaded_model.input_dim_ == model.input_dim_
            assert loaded_model.noise_factor == model.noise_factor
            assert loaded_model.noise_type == model.noise_type

            # Test that loaded model produces same results
            X_transformed_loaded = loaded_model.transform(X)
            np.testing.assert_allclose(
                X_transformed_orig, X_transformed_loaded, rtol=1e-5
            )

    def test_dencdr_errors_unfitted(self, sample_data):
        """Test DENCDR errors when not fitted."""
        X, _ = sample_data
        model = DENCDR(hidden_dims=[16, 8], latent_dim=4)

        with pytest.raises(ValueError, match="not fitted"):
            model.denoise(X)


class TestSENCDR:
    """Test suite for SENCDR class."""

    def test_sencdr_initialization(self):
        """Test SENCDR initialization with default parameters."""
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4)

        assert model.hidden_dims == [16, 8]
        assert model.latent_dim == 4
        assert model.sparsity_weight == 1e-3
        assert model.sparsity_target == 0.05
        assert model.sparsity_type == "kl"
        assert not model.is_fitted_

    def test_sencdr_initialization_custom_params(self):
        """Test SENCDR initialization with custom parameters."""
        model = SENCDR(
            hidden_dims=[64, 32, 16],
            latent_dim=10,
            learning_rate=0.01,
            activation="tanh",
            dropout_rate=0.2,
            weight_decay=1e-4,
            batch_size=64,
            max_epochs=50,
            validation_split=0.1,
            standardize=False,
            random_state=42,
            sparsity_weight=1e-2,
            sparsity_target=0.1,
            sparsity_type="l1",
        )

        assert model.hidden_dims == [64, 32, 16]
        assert model.latent_dim == 10
        assert model.sparsity_weight == 1e-2
        assert model.sparsity_target == 0.1
        assert model.sparsity_type == "l1"

    def test_sencdr_fit(self, sample_data):
        """Test SENCDR fitting."""
        X, _ = sample_data
        model = SENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            validation_split=0.2,
            random_state=42,
        )

        result = model.fit(X)

        assert result is model  # Should return self
        assert model.is_fitted_
        assert model.input_dim_ == 20
        assert model.model_ is not None
        assert model.scaler_ is not None

    def test_sencdr_transform(self, sample_data):
        """Test SENCDR transform without thresholding."""
        X, _ = sample_data
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_transformed = model.transform(X, apply_threshold=False)

        assert X_transformed.shape == (100, 4)
        assert isinstance(X_transformed, np.ndarray)

    def test_sencdr_transform_with_threshold(self, sample_data):
        """Test SENCDR transform with thresholding."""
        X, _ = sample_data
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_sparse = model.transform(X, apply_threshold=True, threshold=0.1)

        assert X_sparse.shape == (100, 4)
        assert isinstance(X_sparse, np.ndarray)
        # Check that small values are zeroed
        assert np.all((np.abs(X_sparse) >= 0.1) | (X_sparse == 0))

    def test_sencdr_get_sparse_features(self, sample_data):
        """Test SENCDR sparse feature extraction."""
        X, _ = sample_data
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        sparse_features = model.get_sparse_features(X, threshold=0.1)

        assert sparse_features.shape == (100, 4)
        assert isinstance(sparse_features, np.ndarray)
        # Check that small values are zeroed
        assert np.all((np.abs(sparse_features) >= 0.1) | (sparse_features == 0))

    def test_sencdr_sparsity_metrics(self, sample_data):
        """Test SENCDR sparsity metrics computation."""
        X, _ = sample_data
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        metrics = model.sparsity_metrics(X)

        assert isinstance(metrics, dict)
        assert "mean_activation" in metrics
        assert "sparsity_ratio" in metrics
        assert "active_neurons" in metrics

        assert isinstance(metrics["mean_activation"], float)
        assert isinstance(metrics["sparsity_ratio"], float)
        assert isinstance(metrics["active_neurons"], float)

        assert 0 <= metrics["sparsity_ratio"] <= 1
        assert metrics["mean_activation"] >= 0
        assert 0 <= metrics["active_neurons"] <= model.latent_dim

    def test_sencdr_predict(self, sample_data):
        """Test SENCDR prediction (reconstruction)."""
        X, _ = sample_data
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)
        X_reconstructed = model.predict(X)

        assert X_reconstructed.shape == X.shape
        assert isinstance(X_reconstructed, np.ndarray)

    def test_sencdr_save_load(self, sample_data):
        """Test SENCDR save and load functionality."""
        X, _ = sample_data
        model = SENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=2,
            sparsity_weight=1e-2,
            sparsity_target=0.1,
            sparsity_type="l1",
            random_state=42,
        )

        model.fit(X)
        X_transformed_orig = model.transform(X)

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_sencdr_model.pkl"
            model.save(filepath)

            # Load model
            loaded_model = SENCDR.load(filepath)

            assert loaded_model.is_fitted_
            assert loaded_model.input_dim_ == model.input_dim_
            assert loaded_model.sparsity_weight == model.sparsity_weight
            assert loaded_model.sparsity_target == model.sparsity_target
            assert loaded_model.sparsity_type == model.sparsity_type

            # Test that loaded model produces same results
            X_transformed_loaded = loaded_model.transform(X)
            np.testing.assert_allclose(
                X_transformed_orig, X_transformed_loaded, rtol=1e-5
            )

    def test_sencdr_errors_unfitted(self, sample_data):
        """Test SENCDR errors when not fitted."""
        X, _ = sample_data
        model = SENCDR(hidden_dims=[16, 8], latent_dim=4)

        with pytest.raises(ValueError, match="not fitted"):
            model.sparsity_metrics(X)

        with pytest.raises(ValueError, match="not fitted"):
            model.get_sparse_features(X)


class TestSpecializedENCDRComparison:
    """Test suite comparing different ENCDR variants."""

    def test_different_encdr_variants_produce_different_results(self, sample_data):
        """Test that different ENCDR variants produce different latent representations."""
        X, _ = sample_data

        # Use same architecture for fair comparison
        common_params = {
            "hidden_dims": [16, 8],
            "latent_dim": 4,
            "max_epochs": 5,
            "random_state": 42,
        }

        # Fit different models
        encdr = ENCDR(**common_params)
        vencdr = VENCDR(**common_params, beta=1.0)
        dencdr = DENCDR(**common_params, noise_factor=0.1)
        sencdr = SENCDR(**common_params, sparsity_weight=1e-3)

        encdr.fit(X)
        vencdr.fit(X)
        dencdr.fit(X)
        sencdr.fit(X)

        # Get transformations
        X_encdr = encdr.transform(X)
        X_vencdr = vencdr.transform(X, use_mean=True)
        X_dencdr = dencdr.transform(X)
        X_sencdr = sencdr.transform(X)

        # All should have same shape
        assert X_encdr.shape == X_vencdr.shape == X_dencdr.shape == X_sencdr.shape

        # But different values (at least some pairs should be different)
        pairs = [
            (X_encdr, X_vencdr),
            (X_encdr, X_dencdr),
            (X_encdr, X_sencdr),
            (X_vencdr, X_dencdr),
            (X_vencdr, X_sencdr),
            (X_dencdr, X_sencdr),
        ]

        different_count = 0
        for arr1, arr2 in pairs:
            if not np.allclose(arr1, arr2, atol=1e-3):
                different_count += 1

        # At least some pairs should be different
        assert different_count > 0, "All ENCDR variants produced identical results"

    def test_vencdr_stochastic_vs_deterministic(self, sample_data):
        """Test VENCDR stochastic vs deterministic behavior."""
        X, _ = sample_data
        model = VENCDR(hidden_dims=[16, 8], latent_dim=4, max_epochs=2, random_state=42)

        model.fit(X)

        # Deterministic transform (use_mean=True) should be consistent
        X_det1 = model.transform(X, use_mean=True)
        X_det2 = model.transform(X, use_mean=True)
        np.testing.assert_allclose(X_det1, X_det2, rtol=1e-6)

        # Stochastic transform (use_mean=False) should be different
        X_stoch1 = model.transform(X, use_mean=False)
        X_stoch2 = model.transform(X, use_mean=False)
        assert not np.allclose(X_stoch1, X_stoch2, atol=1e-6)

    def test_sencdr_sparsity_increases_with_weight(self, sample_data):
        """Test that SENCDR produces sparser representations with higher sparsity weight."""
        X, _ = sample_data

        # Model with low sparsity weight
        model_low = SENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=5,
            sparsity_weight=1e-5,
            random_state=42,
        )

        # Model with high sparsity weight
        model_high = SENCDR(
            hidden_dims=[16, 8],
            latent_dim=4,
            max_epochs=5,
            sparsity_weight=1e-2,
            random_state=42,
        )

        model_low.fit(X)
        model_high.fit(X)

        metrics_low = model_low.sparsity_metrics(X)
        metrics_high = model_high.sparsity_metrics(X)

        # Debug print
        print(f"Low sparsity metrics: {metrics_low}")
        print(f"High sparsity metrics: {metrics_high}")

        # Higher sparsity weight should lead to lower mean activation
        # (sparsity ratio might be 0 for both due to ReLU)
        assert metrics_high["mean_activation"] <= metrics_low["mean_activation"]
