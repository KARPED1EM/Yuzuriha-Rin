# Intent Training Playbooks

This directory now ships notebook-based workflows for the intent predictor that powers `src/services/behavior/sticker.py`. The legacy `.py` scripts have been retired so we can iterate faster inside Jupyter with rich visualizations.

## File overview

1. `01_intent_data_analysis.ipynb`
   - Discovers the project root automatically and loads the corpora from `assets/models/few_shot_intent_sft/data`.
   - Applies blacklist filtering, minimum-sample pruning, balancing, and produces charts (label distribution, text-length stats, heatmaps).
   - Saves the cleaned dataset plus label reports into `assets/models/intent_predictor` so other notebooks stay self-contained.
2. `02_intent_model_training.ipynb`
   - Reuses the processed parquet (or regenerates it when missing), splits the data, and fine-tunes `hfl/chinese-bert-wwm-ext`.
   - Logs huggingface training metrics, plots confusion matrices + per-intent F1 bars, and surfaces the hardest misclassified samples.
   - Persists the model weights, tokenizer files, `intent_mapping.json`, training snapshot, metrics JSON, CSV summaries, and plot PNGs back into `assets/models/intent_predictor`. That directory path stays fixed so the runtime service keeps loading the latest model without code changes.

## Running the notebooks

1. Activate the project virtual environment (`.venv\\Scripts\\activate`) and ensure the toolchain is installed (`pip install -r requirements.txt` if needed). The key dependencies are `transformers`, `datasets`, `torch`, `pandas`, `seaborn`, and `matplotlib`.
2. Launch Jupyter (VS Code, JupyterLab, or `jupyter notebook`) from the repo root so relative paths stay intact.
3. Execute notebook cells sequentially. The notebooks will create any missing folders under `assets/models` and back up existing `assets/models/intent_predictor` contents before overwriting.
4. After training, restart the application – it will pick up the refreshed weights from `assets/models/intent_predictor` automatically.

> Tip: When experimenting with alternative models or hyper-parameters, duplicate the training notebook, tweak the config cell, and keep all artefacts inside `assets/models` to respect the repository layout.
