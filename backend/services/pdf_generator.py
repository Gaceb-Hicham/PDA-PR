"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Générateur de PDF Professionnel v2                                ║
║  Design Universitaire - Université de Boumerdes                              ║
║  Mode PAYSAGE + Largeurs de colonnes adaptées                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
HEADER_RED = colors.HexColor('#7B2D26')
HEADER_DARK = colors.HexColor('#5A1F1A')
BG_CREAM = colors.HexColor('#F5F0E6')
BG_LIGHT = colors.HexColor('#FEFDFB')
TEXT_DARK = colors.HexColor('#2D2D2D')
TEXT_GRAY = colors.HexColor('#666666')
BORDER_LIGHT = colors.HexColor('#D4C4A8')
ROW_ALT = colors.HexColor('#F9F6F0')


def create_styles():
    """Crée les styles de texte professionnels"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='UnivTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HEADER_RED,
        alignment=TA_CENTER,
        spaceAfter=3,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HEADER_RED,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='InfoText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='CellText',
        parent=styles['Normal'],
        fontSize=7,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=9
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=TEXT_GRAY,
        alignment=TA_CENTER
    ))
    
    # Style pour les séparateurs de jours - grande police, blanc, lisible
    styles.add(ParagraphStyle(
        name='DaySeparator',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=14
    ))
    
    return styles


def format_date(date_obj):
    if date_obj:
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%d/%m/%Y')
        return str(date_obj)[:10]
    return ""


def format_time(heure_debut, heure_fin=None):
    if heure_debut:
        start = str(heure_debut)[:5]
        if heure_fin:
            end = str(heure_fin)[:5]
            return f"{start}-{end}"
        return start
    return ""


def truncate(text, max_len=25):
    """Tronque le texte si trop long"""
    text = str(text) if text else ""
    if len(text) > max_len:
        return text[:max_len-2] + ".."
    return text


def create_header(title, info_lines, styles, width=26*cm):
    """Crée l'en-tête du document"""
    elements = []
    
    # Titre
    elements.append(Paragraph(f"· {title} ·", styles['UnivTitle']))
    
    # Infos
    if info_lines:
        info_text = "  |  ".join(info_lines)
        elements.append(Paragraph(info_text, styles['SubTitle']))
    
    # Ligne
    line = Table([[""]],colWidths=[width])
    line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, BORDER_LIGHT)]))
    elements.append(line)
    elements.append(Spacer(1, 8))
    
    return elements


def create_table(headers, data, col_widths, styles, date_col_index=0):
    """Crée un tableau avec séparateurs de jours et text wrapping"""
    cell_style = styles['CellText']
    
    # En-têtes
    header_row = [Paragraph(f"<b>{h}</b>", cell_style) for h in headers]
    
    # Grouper les données par date pour ajouter des séparateurs
    data_rows = []
    separator_indices = []  # Indices des lignes séparateur (1-indexed après header)
    current_date = None
    
    for row in data:
        row_date = row[date_col_index] if date_col_index < len(row) else None
        
        # Si nouvelle date, ajouter un séparateur AVANT les examens de ce jour
        if row_date and row_date != current_date:
            # Créer la ligne séparateur avec style dédié (grande police blanche)
            sep_style = styles.get('DaySeparator', cell_style)
            sep_text = f"<b>📅  {row_date}</b>"
            separator_row = [Paragraph(sep_text, sep_style)] + \
                           [Paragraph("", cell_style) for _ in range(len(headers)-1)]
            data_rows.append(separator_row)
            separator_indices.append(len(data_rows))  # Index après insertion (1-indexed car header=0)
            current_date = row_date
        
        # Ajouter la ligne de données normale
        data_rows.append([Paragraph(str(cell) if cell else "", cell_style) for cell in row])
    
    # Construire le tableau
    table_data = [header_row] + data_rows
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Styles de base
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_RED),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('LINEBELOW', (0, 0), (-1, 0), 1, HEADER_RED),
    ]
    
    # Appliquer styles: séparateurs + alternance couleurs
    row_counter = 0
    for i in range(1, len(table_data)):
        if i in separator_indices:
            # Style séparateur de jour - bandeau coloré fusionné
            style_commands.append(('BACKGROUND', (0, i), (-1, i), HEADER_DARK))
            style_commands.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
            style_commands.append(('SPAN', (0, i), (-1, i)))
            style_commands.append(('ALIGN', (0, i), (-1, i), 'LEFT'))
            style_commands.append(('LEFTPADDING', (0, i), (0, i), 10))
            row_counter = 0  # Reset alternance pour chaque jour
        else:
            # Lignes normales avec alternance de couleurs
            if row_counter % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), BG_LIGHT))
            else:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), ROW_ALT))
            row_counter += 1
    
    table.setStyle(TableStyle(style_commands))
    return table


def create_footer():
    return Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')} • Université de Boumerdes • ExamPro",
        ParagraphStyle('Footer', fontSize=7, textColor=TEXT_GRAY, alignment=TA_CENTER)
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PDF GENERATION - MODE PAYSAGE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_formation_schedule_pdf(formation_name, groupe, niveau, departement, examens):
    """Planning étudiant - PAYSAGE"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                           topMargin=1*cm, bottomMargin=1*cm,
                           leftMargin=1*cm, rightMargin=1*cm)
    styles = create_styles()
    elements = []
    
    # Header
    elements.extend(create_header(
        "Planning des Examens",
        [f"Formation: {formation_name}", f"Groupe: {groupe}", f"Niveau: {niveau}", f"Dept: {departement or '—'}"],
        styles, width=27*cm
    ))
    
    if examens:
        # Étudiants n'ont PAS besoin de voir le surveillant
        headers = ['Date', 'Horaire', 'Code', 'Module', 'Salle']
        data = []
        for exam in examens:
            data.append([
                format_date(exam.get('date')),
                format_time(exam.get('heure_debut'), exam.get('heure_fin')),
                exam.get('module_code', ''),
                truncate(exam.get('module_nom', ''), 40),
                exam.get('salle', '')
            ])
        
        # Colonnes plus larges sans la colonne Surveillant
        col_widths = [3*cm, 3*cm, 2.5*cm, 12*cm, 3*cm]
        elements.append(create_table(headers, data, col_widths, styles))
    
    elements.append(Spacer(1, 15))
    elements.append(create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_professor_schedule_pdf(prof_nom, prof_prenom, departement, surveillances, matricule="", specialite=""):
    """Planning professeur - PAYSAGE"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           topMargin=1*cm, bottomMargin=1*cm,
                           leftMargin=1*cm, rightMargin=1*cm)
    styles = create_styles()
    elements = []
    
    # Header
    info = [f"Professeur: {prof_prenom} {prof_nom}", f"Département: {departement}"]
    if matricule:
        info.append(f"Matricule: {matricule}")
    elements.extend(create_header("Planning de Surveillance", info, styles, width=27*cm))
    
    if surveillances:
        headers = ['Date', 'Horaire', 'Module', 'Formation', 'Grp', 'Dept', 'Salle', 'Rôle']
        data = []
        for s in surveillances:
            data.append([
                format_date(s.get('date')),
                format_time(s.get('heure_debut'), s.get('heure_fin')),
                truncate(s.get('module_nom', s.get('module_code', '')), 25),
                truncate(s.get('formation', ''), 22),
                s.get('groupe', ''),
                truncate(s.get('departement', s.get('dept', '')), 12),
                s.get('salle', ''),
                truncate(s.get('role', ''), 12)
            ])
        
        col_widths = [2.2*cm, 2.2*cm, 5*cm, 5*cm, 1.5*cm, 3*cm, 2*cm, 3*cm]
        elements.append(create_table(headers, data, col_widths, styles))
        
        # Stats
        elements.append(Spacer(1, 8))
        nb_resp = sum(1 for s in surveillances if 'RESP' in str(s.get('role', '')).upper())
        elements.append(Paragraph(
            f"<b>Total: {len(surveillances)} surveillances</b> ({nb_resp} responsable, {len(surveillances)-nb_resp} assistant)",
            styles['InfoText']
        ))
    
    elements.append(Spacer(1, 10))
    elements.append(create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_room_schedule_pdf(salle_nom, salle_code, capacite, examens, salle_type="", batiment=""):
    """Planning salle - PAYSAGE"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           topMargin=1*cm, bottomMargin=1*cm,
                           leftMargin=1*cm, rightMargin=1*cm)
    styles = create_styles()
    elements = []
    
    # Header
    info = [f"Salle: {salle_nom} ({salle_code})", f"Capacité: {capacite} places"]
    if salle_type:
        info.append(f"Type: {salle_type}")
    if batiment:
        info.append(f"Bâtiment: {batiment}")
    elements.extend(create_header("Planning de la Salle", info, styles, width=27*cm))
    
    if examens:
        headers = ['Date', 'Horaire', 'Module', 'Formation', 'Grp', 'Surveillant', 'Étudiants']
        data = []
        for e in examens:
            surv = e.get('surveillant') or e.get('prof_nom') or ''
            data.append([
                format_date(e.get('date')),
                format_time(e.get('heure_debut'), e.get('heure_fin')),
                truncate(e.get('module_nom', e.get('module_code', '')), 25),
                truncate(e.get('formation', ''), 22),
                e.get('groupe', ''),
                truncate(surv, 18),
                str(e.get('nb_etudiants', '—'))
            ])
        
        col_widths = [2.2*cm, 2.2*cm, 5*cm, 5*cm, 1.5*cm, 4.5*cm, 2*cm]
        elements.append(create_table(headers, data, col_widths, styles))
        
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>Total: {len(examens)} examens planifiés</b>", styles['InfoText']))
    
    elements.append(Spacer(1, 10))
    elements.append(create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_department_schedule_pdf(dept_name, formations_data, session_name="Session actuelle"):
    """Planning département - PAYSAGE avec toutes formations"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           topMargin=1*cm, bottomMargin=1*cm,
                           leftMargin=1*cm, rightMargin=1*cm)
    styles = create_styles()
    elements = []
    
    # Page de garde
    elements.append(Spacer(1, 3*cm))
    elements.append(Paragraph(f"· Planning des Examens ·", styles['UnivTitle']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Département: {dept_name}", styles['SectionHeader']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Session: {session_name}", styles['SubTitle']))
    elements.append(Spacer(1, 1*cm))
    
    # Liste formations
    nb_formations = len(formations_data)
    total_exams = sum(len(d.get('exams', [])) for d in formations_data.values())
    elements.append(Paragraph(f"<b>{nb_formations} formations • {total_exams} créneaux d'examen</b>", styles['InfoText']))
    elements.append(Spacer(1, 3*cm))
    elements.append(create_footer())
    elements.append(PageBreak())
    
    # Une page par formation
    for formation_name, data in formations_data.items():
        niveau = data.get('niveau', '')
        examens = data.get('exams', [])
        
        if not examens:
            continue
        
        elements.extend(create_header(
            "Planning des Examens",
            [f"Formation: {formation_name}", f"Niveau: {niveau}", f"Dept: {dept_name}"],
            styles, width=27*cm
        ))
        
        # Planning département: sans surveillant (public: étudiants/administration)
        headers = ['Date', 'Horaire', 'Code', 'Module', 'Groupe', 'Salle']
        table_data = []
        for e in examens:
            table_data.append([
                format_date(e.get('date')),
                format_time(e.get('heure_debut'), e.get('heure_fin')),
                e.get('module_code', ''),
                truncate(e.get('module_nom', ''), 35),
                e.get('groupe', 'G01'),
                e.get('salle', '')
            ])
        
        col_widths = [3*cm, 2.5*cm, 2.5*cm, 10*cm, 2*cm, 3*cm]
        elements.append(create_table(headers, table_data, col_widths, styles))
        elements.append(Spacer(1, 10))
        elements.append(create_footer())
        elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


# Aliases
def generate_student_schedule_pdf(formation_name, groupe, niveau, examens, departement=""):
    return generate_formation_schedule_pdf(formation_name, groupe, niveau, departement, examens)

def generate_multi_group_pdf(formation_name, niveau, exams_by_group, departement=""):
    """
    Génère UN PDF avec une PAGE SÉPARÉE pour chaque groupe.
    Chaque page contient: Formation, Groupe, Niveau, et liste des examens.
    """
    from reportlab.platypus import PageBreak
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           topMargin=1*cm, bottomMargin=1*cm,
                           leftMargin=1*cm, rightMargin=1*cm)
    styles = create_styles()
    elements = []
    
    # Trier les groupes
    sorted_groups = sorted(exams_by_group.keys())
    
    for idx, groupe in enumerate(sorted_groups):
        examens = exams_by_group[groupe]
        
        # Header pour ce groupe
        elements.extend(create_header(
            "Planning des Examens",
            [
                f"Formation: {formation_name}",
                f"Groupe: {groupe}",
                f"Niveau: {niveau}",
                f"Département: {departement or '—'}"
            ],
            styles, width=27*cm
        ))
        
        if examens:
            # Étudiants n'ont PAS besoin de voir le surveillant
            headers = ['Date', 'Horaire', 'Code', 'Module', 'Salle']
            data = []
            for exam in examens:
                data.append([
                    format_date(exam.get('date')),
                    format_time(exam.get('heure_debut'), exam.get('heure_fin')),
                    exam.get('module_code', ''),
                    truncate(exam.get('module_nom', ''), 40),
                    exam.get('salle', '')
                ])
            
            col_widths = [3*cm, 3*cm, 2.5*cm, 12*cm, 3*cm]
            elements.append(create_table(headers, data, col_widths, styles))
        else:
            elements.append(Paragraph("Aucun examen programmé", styles['Normal']))
        
        elements.append(Spacer(1, 15))
        elements.append(create_footer())
        
        # Saut de page sauf pour le dernier groupe
        if idx < len(sorted_groups) - 1:
            elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_department_pdf(dept_name, formations_data, session_name="Session actuelle"):
    return generate_department_schedule_pdf(dept_name, formations_data, session_name)
