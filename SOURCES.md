# Sources and licensing

This skill is an original fusion written for this workspace in November 2026. It combines two upstream skills, studied file by file from local clones kept in workspace/research/image-prompt-reverse-compare/:

- LunarXuan/image-prompt-reverse (857 stars at study time, GPL-3.0). Source of the analysis kernel: the general analysis framework, the category guide system including the illustration content and style decoupling method, the media boundary rules, the IP and text handling rules, the visual anchor discipline, and the recreation output format of a 450 to 700 character Chinese prompt, an English equivalent, and 10 to 15 targeted negatives. The GPL-3.0 LICENSE file from that repository is included in this folder and covers the derived material.
- The image-style-reverse-engineer skill inside Zemon-tech/contentCreationAgent (no license file in that repository at study time). Source of the visible structured report idea, the style-only mode that strips the subject and keeps transferable style DNA, the palette of five HEX values, the Kelvin and contrast-ratio taxonomy data, and the practice of shipping a validator script and a worked example. Its forced-specifics rule, which required a concrete focal length, Kelvin value and film stock for every image, was deliberately not carried over: this skill grades such values as inferred, writes them as tildes or ranges, and pairs them with the visible effects that ground them.

Factual reference data such as Kelvin ranges, contrast ratios and film stock characteristics are standard photographic knowledge and are stated as such in references/light-and-color-vocabulary.md.

Upstream repositories:
- https://github.com/LunarXuan/image-prompt-reverse
- https://github.com/Zemon-tech/contentCreationAgent
