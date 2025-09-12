import os
import sys
from pix2tex.cli import LatexOCR
from pathlib import Path

# --- Configuration ---
# Define the target directory for the model weights.
# This path should align with the volume mount in your docker-compose.yml.
MODEL_PATH = Path("./models/latexocr-model")

def download_model():
    """
    Initializes the LatexOCR model which triggers the download of the weights
    to the default cache directory. We then move it to our desired location.
    """
    print("Initializing LatexOCR to trigger model download...")
    
    # Temporarily set the cache dir if needed, but pix2tex is good at finding it.
    # The model will be downloaded to a path like:
    # ~/.cache/torch/hub/checkpoints/ or a similar location.
    # The LatexOCR object knows where to find its weights.
    
    try:
        # This line triggers the download if the model is not found in cache.
        model = LatexOCR()
        
        # The weights are typically stored in a path managed by torch.hub
        # We need to find where the default weights file is.
        # The default weights file is usually 'weights.pth'.
        # Let's find it in the package's model directory.
        
        import pix2tex
        package_path = Path(pix2tex.__file__).parent
        default_checkpoint_path = package_path / "model/checkpoints/weights.pth"

        if not default_checkpoint_path.exists():
             print(f"Could not automatically find the downloaded weights at {default_checkpoint_path}")
             print("Please ensure the model has been downloaded by running this script with internet access.")
             # As a fallback, let's try the torch hub cache path
             torch_hub_dir = Path(os.getenv("TORCH_HOME", Path.home() / ".cache/torch")) / "hub/checkpoints"
             alt_checkpoint_path = torch_hub_dir / "weights.pth" # This might vary
             if alt_checkpoint_path.exists():
                 default_checkpoint_path = alt_checkpoint_path
             else:
                 print(f"Also could not find weights in {torch_hub_dir}. Exiting.")
                 sys.exit(1)


        print(f"Found model weights at: {default_checkpoint_path}")

        # --- Create target directory and move the model ---
        MODEL_PATH.mkdir(parents=True, exist_ok=True)
        
        target_file = MODEL_PATH / "weights.pth"
        
        if target_file.exists():
            print(f"Model already exists at {target_file}. Skipping copy.")
        else:
            import shutil
            print(f"Copying model weights to {target_file}...")
            shutil.copy(default_checkpoint_path, target_file)
            print("Model copied successfully.")

        print("\n--- Setup Complete ---")
        print(f"Model weights are now located in: {MODEL_PATH.resolve()}")
        print("Please ensure your docker-compose.yml correctly mounts this directory.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your internet connection and permissions.")
        sys.exit(1)

if __name__ == "__main__":
    download_model()