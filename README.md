# Temporal-expression-normalization-with-fill-mask

This repo corresponds to the paper ["A Novel Methodology for Enhancing Cross-Language and Domain Adaptability in Temporal Expression Normalization"] (https://direct.mit.edu/coli/article/doi/10.1162/COLI.a.12/130701).

For using the code, please refer to the README.md in the code folder.


## Citation

@article{10.1162/COLI.a.12,
    author = {Sánchez de Castro, Alejandro and Araujo, Lourdes and Martinez-Romo, Juan},
    title = {A Novel Methodology for Enhancing Cross-Language and Domain Adaptability in Temporal Expression Normalization},
    journal = {Computational Linguistics},
    pages = {1-32},
    year = {2025},
    month = {05},
    abstract = {Accurate temporal expression normalization, the process of assigning a numerical value to a temporal expression, is essential for tasks such as timeline creation and temporal reasoning. While rule-based normalization systems are limited in adaptability across different domains and languages, deep-learning solutions in this area have not been extensively explored. An additional challenge is the scarcity of manually annotated corpora with temporal annotations. To address the adaptability limitations of current systems, we propose a highly adaptable methodology that can be applied to multiple domains and languages. This can be achieved by leveraging a multilingual Pre-trained Language Model (PTLM) with a fill-mask architecture, using a Value Intermediate Representation (VIR) where the temporal expression value format is adjusted to the fill-mask representation. Our approach involves a two-phase training process. Initially, the model is trained with a novel masking policy on a large English biomedical corpus that is automatically annotated with normalized temporal expressions, along with a complementary hand-crafted temporal expressions corpus. This addresses the lack of manually annotated data and helps to achieve sufficient capacity for adaptation to diverse domains or languages. In the second phase, we show how the model can be tailored to different domains and languages employing various techniques, showcasing the versatility of the proposed methodology. This approach significantly outperforms existing systems.},
    issn = {0891-2017},
    doi = {10.1162/COLI.a.12},
    url = {https://doi.org/10.1162/COLI.a.12},
    eprint = {https://direct.mit.edu/coli/article-pdf/doi/10.1162/COLI.a.12/2523155/coli.a.12.pdf},
}



