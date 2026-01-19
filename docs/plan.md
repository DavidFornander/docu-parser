This response provides a strict, implementation-level blueprint for building the **Ingestion and Completeness Engine** described in "Notebook A" (Source 1: *Architectural Blueprint for Deterministic Knowledge Synthesis*).

It translates the theoretical goals of "Glass Box Ingestion" and "Deterministic Verification" into executable engineering tasks, utilizing the specific tool stacks identified in the supporting technical reports [Source: 4, 5, 7].

### **Phase 1: The "Canonical" Pre-Processing Layer**

**Goal:** Establish a unified coordinate system. Source 1 mandates handling heterogeneity (DOCX, HTML) by normalizing to a single format to enable "Spatial Binding" [Source: 17, 18].

**Zero-Abstraction Implementation:**
You do not build separate parsers for every file type. You force a "Canonical PDF" workflow.

1. **Deploy a Headless Conversion Service:**
* Use **LibreOffice** in headless mode for robust DOCX/PPTX to PDF conversion. It preserves the exact layout coordinates required for the "Glass Box" audit.
* **Command:**
```bash
libreoffice --headless --convert-to pdf --outdir /ingest_buffer /raw_input/*.docx

```


* *Why:* This ensures that every input document, regardless of origin, has a fixed `(x, y)` coordinate system for its text, which is the prerequisite for "Source Tracing" [Source: 17].



---

### **Phase 2: The "Glass Box" Extraction (Layout-Aware Parsing)**

**Goal:** Extract text while preserving "Spatial Logic" (bounding boxes, font hierarchies) to avoid the "Serialization Fallacy" [Source: 11].

**Implementation Stack:**
Source 1 describes "LayoutRL" and "Infinity-Parser." The production-ready open-source implementation of these principles (layout-aware, deep-learning based) is **Marker** combined with **Surya** [Source: 455, 456].

#### **Step 2.1: Primary Extraction (Marker Pipeline)**

Do not use `PyPDF2` or `Tesseract`. They destroy layout.

1. **Install Marker:**
* Requires a GPU (NVIDIA, 8GB+ VRAM recommended).
* `pip install marker-pdf`


2. **Execution Command:**
* Run the extraction with `force_ocr` to handle embedded images/charts and `batch_multiplier` to saturate your GPU.


```bash
marker_single /path/to/canonical.pdf /output_dir \
  --batch_multiplier 2 \
  --langs English \
  --force_ocr

```


3. **Output Processing:**
* Marker outputs a JSON file containing specific blocks. You must parse this JSON, not just the Markdown.
* **Key Data to Extract:**
* `block_type`: (e.g., "Table", "Equation", "Title").
* `polygon`: The specific `[x, y]` coordinates of the block. **Store this.** This is your "Glass Box" trace.
* `content`: The text/LaTeX.





#### **Step 2.2: The "Dense Math" Fallback (Nougat)**

Source 1 and 5 emphasize that standard OCR mangles complex calculus [Source: 339]. You need a fallback route.

1. **Logic Gate:**
* Scan the Marker output. If the density of LaTeX delimiters (`$`, `\begin{equation}`) in a block is high but the confidence score is low, route that specific page to **Nougat**.


2. **Nougat Execution:**
* `pip install nougat-ocr`
* Command:
```bash
nougat /path/to/canonical.pdf -o /output_dir -p [specific_page_number]

```


* *Note:* Nougat is slower (3s/page) [Source: 573]. Only use it for pages where Marker fails the "Math Density" check.



---

### **Phase 3: The Completeness Audit (The "Gap-Filling" Loop)**

**Goal:** The "Completeness Audit" mandates that the machine *prove* it captured everything [Source: 22]. This is the "Reverse RAG" protocol [Source: 210].

**Zero-Abstraction Implementation:**
You must build a recursive Python loop that does not proceed until a "Coverage Score" > 99%.

#### **Step 3.1: Atomic Claim Extraction**

Break the extracted text into testable atomic claims.

* **Tool:** Local LLM (Llama-3-8B-Instruct via Ollama).
* **Prompt:**
> "Break the following text block into a list of atomic, indivisible facts. Return ONLY a JSON list of strings."


* **Input:** The text block from Marker.
* **Output:** `["The Eiffel Tower is in Paris.", "It is 330m tall."]`

#### **Step 3.2: The "Reverse Query" (Source Matching)**

Verify these claims exist in the raw source vector space.

1. **Vector Store:** Use **LanceDB** (embedded, zero-copy) [Source: 593].
2. **Embedding:** Use **BGE-M3** (handles dense retrieval well) [Source: 595].
3. **The Check:**
* Embed the *original* PDF page text (using a sliding window).
* Embed the *extracted* atomic claims.
* Perform a similarity search.
* **Metric:** If `Max_Similarity(Claim_Vector, Source_Vectors) < 0.85`, flag as **Potential Hallucination** or **Information Loss**.



#### **Step 3.3: The Recursive "Gap-Filling" Protocol**

This is the "Gap-Filling Loop" described in Source 1 [Source: 30].

**Python Logic (Pseudo-code):**

```python
def gap_filling_loop(source_page_img, extracted_text):
    # 1. Audit
    missing_claims = audit_completeness(source_page_img, extracted_text)
    
    if not missing_claims:
        return extracted_text # Deterministic Success
    
    # 2. Identification (Visual Bounding Box)
    # Use Layout Analysis (Surya) to find the box covering the missing info
    target_box = find_missing_region(source_page_img, missing_claims)
    
    # 3. Re-Ingestion (Zoom In)
    # Crop the image to that specific box
    cropped_img = source_page_img.crop(target_box)
    
    # 4. Targeted Prompt
    new_fact = vlm_client.query(
        image=cropped_img, 
        prompt=f"Extract the specific details regarding {missing_claims} from this region."
    )
    
    # 5. Integration
    return merge(extracted_text, new_fact)

```

* **Hardware:** Use a VLM like **LLaVA-v1.6** (local via Ollama) for the "Re-Ingestion" step [Source: 588]. It can "see" the chart/table you missed and transcribe it.

---

### **Phase 4: Ontology-Driven Knowledge Graph Construction**

**Goal:** Convert text to a structure guided by a strict Domain Ontology [Source: 33, 34].

**Implementation:**
Source 1 suggests **GLiNER** (Generalist Lightweight Named Entity Recognition) [Source: 34]. This is superior to standard LLM extraction because it is zero-shot and strictly typed.

1. **Define Ontology:**
* Create a list of labels: `["Concept", "Theorem", "Prerequisite", "Example", "Constraint"]`.


2. **Run GLiNER:**
* `pip install gliner`
* Load model: `urchade/gliner_medium-v2.1`
* **Execution:**
```python
from gliner import GLiNER
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
labels = ["Concept", "Theorem", "Metric"]
entities = model.predict_entities(extracted_text, labels)

```




3. **Bind to Coordinates:**
* Take the entities from GLiNER.
* Map them back to the `polygon` coordinates from the Marker JSON.
* **Result:** A node in your graph database (Neo4j) that looks like:
```json
{
  "id": "Theorem_3.1",
  "type": "Theorem",
  "text": "...",
  "source_loc": {"page": 12, "bbox": [100, 200, 500, 600]} 
}

```


* This "source_loc" binding is the "Golden Thread" required for the **Glass Box** system [Source: 37].



### **Summary of the "Notebook A" Build Stack**

| Component | Abstract Requirement (Source 1) | Concrete Tool (Source 4, 5) | Action |
| --- | --- | --- | --- |
| **Canonical Input** | "Unified Conversion" | **LibreOffice (Headless)** | Normalize docx/html to PDF. |
| **Parsing** | "Layout-Aware / LayoutRL" | **Marker + Surya** | Extract text + Bounding Boxes. |
| **Math Fallback** | "High Fidelity" | **Nougat** | Retry failed math blocks. |
| **Audit** | "Atomic Claim Recall" | **Llama-3 + LanceDB** | Reverse RAG verification loop. |
| **Gap Filling** | "Recursive Zoom" | **LLaVA (VLM)** | Re-read specific image crops. |
| **Structure** | "Ontology Extraction" | **GLiNER** | Extract strictly typed entities. | 
