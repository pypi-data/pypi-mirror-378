# Changelog

## [stormi-v0.7.0](https://github.com/pinellolab/stormi/compare/stormi-v0.6.1...stormi-v0.7.0) (2025-09-22)

### Features

* **AmortizedNormal:** Prediction of cell path weights, optional consideration of technical batches, optional hidden layer in amortized net and optional warmup for ATAC detection efficiency ([05bb1c8](https://github.com/pinellolab/stormi/commit/05bb1c8203625196a35e59506249a9842f70d917))
* **evaluation:** add `auc_preprocess`and `plot_AUC` functions. ([e7a4263](https://github.com/pinellolab/stormi/commit/e7a426376bab378f600a95d7351a8190e25fb77e))
* **extract_posterior_means:** Added compatibility with ATAC models and Amortized Guides that acccount for experimental batch and finally added option to also extract numpyro parameters, rather than just sample sites. ([b4f76de](https://github.com/pinellolab/stormi/commit/b4f76deb106bb584a6f4e98f0dbaf74ff10c6dcd))
* **models:** New ATAC RNA model. ATAC is non-linear function of (motif-filtered) TF input and gene transcription rates are linear function of nearby region accessibilities. After training linearization functions can provide a linear GRN for each cell type. ([203c16c](https://github.com/pinellolab/stormi/commit/203c16c6df212f65b72f21edb968c6de5495390b))
* **models:** New MultiLineage model for RNA data with pulse shaped noise term ([1b354fe](https://github.com/pinellolab/stormi/commit/1b354fe44a1fc4d0dc617ba3c19be5fac9ce3bff))
* **models:** Updated Readme to clarify which model is the latest for each use case. ([5b1879c](https://github.com/pinellolab/stormi/commit/5b1879c01c1c52eb17b3eba4a9b3886cd8caf1bd))
* **plotting:** New posterior_data_geneset function that works with new models that have different normalization strategy. Old function still included for compatibility with old models. ([d3ba6f9](https://github.com/pinellolab/stormi/commit/d3ba6f95b8fcd6657505dd292823f97d43780148))
* **plotting:** New posterior_data_geneset_with_accessiblity function that plots trajectories of both RNA and highly associated regions for a given gene. ([0c1d6f2](https://github.com/pinellolab/stormi/commit/0c1d6f29eb9cfcb5f80137f74e197db0ba99f74e))
* **RNA_2layers_ManualEuler:** Linearization Utilities can extract a linear GRN in each cell type after training for easier interpretation. ([b30562a](https://github.com/pinellolab/stormi/commit/b30562a2089bb114e00200407b2b17660938114c))
* **stormi:** Added an evaluation module, where we can add quantitative evaluation metrics and plotting functions that can be used after training the models. ([91cb294](https://github.com/pinellolab/stormi/commit/91cb29443597647e19096abb98710d4669d18be9))
* **tests:** Tests for ATAC model and linearization ([6e1763a](https://github.com/pinellolab/stormi/commit/6e1763a34cd3d35218f972503ebfa20530b57b8a))
* **train:** Made JIT training functions compatible with ATAC models. ([5e1b543](https://github.com/pinellolab/stormi/commit/5e1b5430231da9d8321f13924d26f3fd0dd7dc31))

### Bug Fixes

* **AmortizedSplicing:** Added batch and cell number parameter to extract_all_means function to ensure same function signature as in the new AmortizedNormal Guide, and thus removing a test error. ([d3b4918](https://github.com/pinellolab/stormi/commit/d3b4918e6d6c9cf8037895eb028199046d4243f1))
* **RNA_2layers_MultiplePaths_SDE.py:** Added optional kwargs for compatibility with both RNA and ATAC JIT training function and to address test error. ([60360f4](https://github.com/pinellolab/stormi/commit/60360f4c6235428b53264cba8d3f990035885a1f))
* **tests:** Modified ATAC tests to fit new training function ([2fbae46](https://github.com/pinellolab/stormi/commit/2fbae46d54c988eb2910d98f8e0db0570907ab50))
