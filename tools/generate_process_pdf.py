from pathlib import Path
from textwrap import dedent

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "human_cell_digital_twin_process_library.pdf"
PLAN_IMAGE = Path("/Users/saha/Downloads/6week_execution_plan.png")


PROCESS_FILES = [
    ("Process 1", "Membrane Transport", "p01_transport.py"),
    ("Process 2", "Glycolysis", "p02_glycolysis.py"),
    ("Process 3", "Oxidative Phosphorylation", "p03_oxphos.py"),
    ("Process 4", "Fermentation", "p04_fermentation.py"),
    ("Process 5", "ATP Demand", "p05_atp_demand.py"),
    ("Process 6", "HIF-1a Oxygen Sensing", "p06_hif1a.py"),
    ("Process 7", "Calcium Signalling", "p07_calcium.py"),
    ("Process 8", "mTOR Protein Synthesis", "p08_mtor.py"),
    ("Process 9", "Na/K-ATPase Pump", "p09_nakpump.py"),
]


PROCESS_SUMMARIES = {
    "Process 1": {
        "purpose": "Imports glucose and oxygen, and models passive sodium leak across the membrane. HIF-1a scales GLUT activity under hypoxia.",
        "equations": [
            "v_glut = Vmax_glut * glut_scale * Glc_ext / (Km_glut + Glc_ext)",
            "v_o2 = Vmax_o2 * O2_ext / (Km_o2 + O2_ext)",
            "glut_scale = 1 + (HIF_MAX_GLUT - 1) * hif1a",
        ],
    },
    "Process 2": {
        "purpose": "Converts cytosolic glucose into pyruvate and a small amount of ATP. ADP activates the flux, approximating PFK demand coupling.",
        "equations": [
            "v_glyc = Vmax_glyc * Glc / (Km_glc + Glc) * ADP / (Km_adp + ADP)",
            "Glucose -> 2 Pyruvate + 2 ATP",
        ],
    },
    "Process 3": {
        "purpose": "Uses pyruvate and oxygen to produce the main ATP supply under normoxia.",
        "equations": [
            "v_oxphos = Vmax_oxphos * Pyr / (Km_pyr + Pyr) * O2 / (Km_o2 + O2)",
            "Pyruvate + 3 O2 -> 30 ATP",
        ],
    },
    "Process 4": {
        "purpose": "Converts pyruvate to lactate when oxygen is low. HIF-1a increases fermentation capacity during hypoxia.",
        "equations": [
            "o2_inhibition = 1 - O2 / (Km_o2_inh + O2)",
            "v_ferm = Vmax_ferm * ferm_scale * Pyr / (Km_pyr + Pyr) * o2_inhibition",
            "ferm_scale = 1 + (HIF_MAX_FERM - 1) * hif1a",
        ],
    },
    "Process 5": {
        "purpose": "Represents housekeeping ATP use by processes not explicitly modeled.",
        "equations": [
            "v_demand = ATP_DEMAND_BASE * ATP / (Km_demand + ATP)",
            "ATP -> ADP",
        ],
    },
    "Process 6": {
        "purpose": "Models the oxygen-sensitive HIF-1a switch that couples hypoxia to glucose import and fermentation.",
        "equations": [
            "if O2 < HIF_O2_THRESH: dHIF/dt = k_rise * (1 - HIF)",
            "else: dHIF/dt = -k_fall * HIF",
            "HIF is clamped to [0, 1]",
        ],
    },
    "Process 7": {
        "purpose": "Maintains low resting cytosolic calcium using a leak plus pump homeostasis model.",
        "equations": [
            "v_leak = CA_LEAK_RATE",
            "v_pump = CA_PUMP_RATE * max(Ca_cyt - CA_REST, 0)",
            "dCa/dt = v_leak - v_pump",
        ],
    },
    "Process 8": {
        "purpose": "Links ATP abundance and amino acids to protein synthesis through an mTOR-like anabolic gate.",
        "equations": [
            "mTOR_activity = clamp(ATP / NORMAL_ATP, 0, 1)",
            "v_synth = Vmax_ribo * mTOR_activity * ATP / (Km_atp + ATP) * AA / (Km_aa + AA)",
            "4 ATP + 1 amino acid -> 1 protein_mass unit + 4 ADP",
        ],
    },
    "Process 9": {
        "purpose": "Models Na/K-ATPase as a major ATP consumer that maintains sodium and potassium gradients.",
        "equations": [
            "v_pump = Vmax_pump * pump_activity * mm(ATP) * Hill(Na_cyt, Km_Na, 3) * Hill(K_ext, Km_K, 2)",
            "1 ATP + 3 Na_cyt + 2 K_ext -> ADP + 3 Na_ext + 2 K_cyt",
        ],
    },
}


def source_excerpt(filename):
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    lines = []
    in_body = False
    for line in text.splitlines():
        if line.strip().startswith("def compute"):
            in_body = True
        if in_body:
            lines.append(line)
        if in_body and len(lines) > 0 and line.strip() == "return s":
            break
    excerpt = "\n".join(lines).strip()
    return excerpt if excerpt else text[:1200]


def para(text, style):
    return Paragraph(text.replace("&", "&amp;"), style)


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=colors.HexColor("#163B3A"),
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#4C5C5C"),
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#155C55"),
            spaceBefore=10,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#253B54"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13.2,
            textColor=colors.HexColor("#222222"),
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#444444"),
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=6.8,
            leading=8.2,
            leftIndent=5,
            rightIndent=5,
            textColor=colors.HexColor("#17202A"),
            backColor=colors.HexColor("#F4F7F7"),
            borderPadding=5,
            borderColor=colors.HexColor("#CBD9D8"),
            borderWidth=0.4,
            spaceBefore=4,
            spaceAfter=7,
        ),
    }


def bullet_items(items, style):
    story = []
    for item in items:
        story.append(para(f"- {item}", style))
    return story


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#66706F"))
    canvas.drawString(0.65 * inch, 0.38 * inch, "Human Cell Digital Twin - Process Library")
    canvas.drawRightString(7.85 * inch, 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    styles = build_styles()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        rightMargin=0.58 * inch,
        leftMargin=0.58 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.62 * inch,
    )

    story = []
    story.append(para("Human Cell Digital Twin", styles["title"]))
    story.append(para("Core process descriptions, governing equations, and implementation blocks", styles["subtitle"]))

    intro = dedent(
        """
        You built a minimum viable biological simulation for a human-cell digital twin. The current code is a compartmental ODE model: one state dictionary holds molecule concentrations, each process computes a flux for one time step, and the main loop applies those fluxes in biological order. The model is designed to become spatial by running the same reaction equations independently in each voxel and adding a diffusion Laplacian.
        """
    ).strip()
    story.append(para(intro, styles["body"]))

    story.append(para("What Exists So Far", styles["h1"]))
    table_rows = [
        ["Layer", "Files", "Role"],
        ["Parameters", "constants.py", "Central kinetic constants, time step, duration, and process rates."],
        ["State", "state.py", "Initial mM concentrations for ATP, ADP, glucose, oxygen, ions, calcium, amino acids, protein mass, and HIF-1a."],
        ["Math helpers", "helpers.py", "Clamp, Michaelis-Menten saturation, and Hill functions."],
        ["Processes", "p01...p09", "Nine biological flux modules with compute/apply functions."],
        ["Runner", "simulate.py", "Scenario controller and process ordering for normal, hypoxia, and starvation runs."],
        ["QA/viz", "validate.py, plot.py", "Sanity checks and time-series plots for the hypoxia demo."],
    ]
    table_data = [[para(cell, styles["small"]) for cell in row] for row in table_rows]
    table = Table(table_data, colWidths=[1.0 * inch, 1.25 * inch, 4.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEFED")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#143A37")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B5C7C5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFA")]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8))

    story.append(para("Current Implementation Note", styles["h2"]))
    story.append(
        para(
            "The process filenames have been normalized to Python-importable module names, matching simulate.py. The simulation runs, and the current validation status is 10/10 checks passing after making GLUT reversible and ADP-limiting ATP-producing reactions.",
            styles["body"],
        )
    )

    if PLAN_IMAGE.exists():
        story.append(PageBreak())
        story.append(para("Six-Week Execution Plan", styles["h1"]))
        story.append(
            para(
                "The plan keeps the deliverable intentionally narrow: nine process ODEs, HIF-1a hypoxia coupling, a 3-D reaction-diffusion grid, GPU scaling, WebGL volume rendering, and a hypoxia demo. Calcium, apoptosis, transcription/translation, Poisson electrostatics, waste/autophagy, and cytoplasmic flow are explicitly deferred.",
                styles["body"],
            )
        )
        img = Image(str(PLAN_IMAGE))
        img._restrictSize(6.9 * inch, 8.8 * inch)
        story.append(img)

    story.append(PageBreak())
    story.append(para("Core Processes", styles["h1"]))
    for proc_id, title, filename in PROCESS_FILES:
        summary = PROCESS_SUMMARIES[proc_id]
        block = [
            para(f"{proc_id}: {title}", styles["h2"]),
            para(summary["purpose"], styles["body"]),
            para("Governing equations:", styles["small"]),
        ]
        block.extend(bullet_items(summary["equations"], styles["small"]))
        block.append(para("Implementation excerpt:", styles["small"]))
        block.append(Preformatted(source_excerpt(filename), styles["code"]))
        story.append(KeepTogether(block))

    story.append(PageBreak())
    story.append(para("Spatial Extension", styles["h1"]))
    story.append(
        para(
            "The next architectural step is to replace one scalar concentration per molecule with a 3-D array per molecule. Each voxel evaluates the same local reaction equations and also exchanges material with its six face-neighbor voxels through a finite-difference Laplacian.",
            styles["body"],
        )
    )
    spatial_eqs = [
        "dC/dt = D * Laplacian(C) + R(C)",
        "Laplacian(C) = (C[x+1] + C[x-1] + C[y+1] + C[y-1] + C[z+1] + C[z-1] - 6*C[x,y,z]) / dx^2",
        "dATP/dt = D_ATP*Lap(ATP) + v_oxphos - v_demand - v_synth - v_pump",
        "dO2/dt = D_O2*Lap(O2) + v_import - 3*v_oxphos",
        "dGlucose/dt = D_Glc*Lap(Glucose) + v_glut - v_glycolysis",
        "dLactate/dt = D_Lac*Lap(Lactate) + v_fermentation - v_export",
    ]
    story.extend(bullet_items(spatial_eqs, styles["body"]))

    shader = dedent(
        """
        // One GPU invocation per voxel
        pos = global_invocation_id
        atp = readATP(pos)
        lap_atp = (readATP(pos+X) + readATP(pos-X)
                 + readATP(pos+Y) + readATP(pos-Y)
                 + readATP(pos+Z) + readATP(pos-Z)
                 - 6.0 * atp) / (dx * dx)

        oxphos = compute_oxphos(pyr, o2, adp)
        synth = compute_mTOR_synth(atp, amino_acids)
        pump = compute_NaK_pump(atp, sodium, potassium_ext)

        d_atp = D_ATP * lap_atp + oxphos - demand - synth - pump
        writeATP_next(pos, atp + d_atp * sub_dt)
        """
    ).strip()
    story.append(Preformatted(shader, styles["code"]))

    story.append(para("How To Continue", styles["h1"]))
    next_steps = [
        "Run simulate.py, validate.py, and plot.py after each biology or parameter change.",
        "Refine oxygen handling by making O2 exchange concentration-gradient driven, the same way GLUT is now reversible.",
        "Run normal, hypoxia, and starvation validations; tune only after preserving expected qualitative behavior.",
        "Add a 1-D oxygen diffusion prototype with the same Fick/Laplacian update before jumping to 3-D.",
        "Promote scalar state variables to small 32^3 NumPy arrays and graft the existing process functions over voxel arrays.",
        "Add membrane/boundary masks so transport only occurs at the cell surface while metabolism occurs inside the cell.",
        "Use explicit Euler sub-stepping with dt < dx^2 / (2 * D_max), then move the stencil to CuPy/CUDA or WGSL.",
        "Connect WebGL/three.js to 3-D textures for ATP, O2, lactate, Na_cyt, and protein_mass.",
        "Make the final demo an interactive hypoxia scenario: lower external O2, show HIF-1a rise, lactate accumulation, ATP stress, pump failure, and recovery.",
    ]
    story.extend(bullet_items(next_steps, styles["body"]))

    story.append(para("Deferred Scope", styles["h1"]))
    story.append(
        para(
            "For a six-week MVP, keep calcium spikes, apoptosis/cell fate, transcription/translation detail, autophagy, Stokes flow, and Poisson electrostatics out of the required deliverable. Mention them as future work after the WebGL spatial hypoxia demo is stable.",
            styles["body"],
        )
    )

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return OUT


if __name__ == "__main__":
    print(build_pdf())
