"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Générateur de PDF Professionnel                                   ║
║  Design Universitaire - Université de Boumerdes                              ║
║  Colonnes: Date, Jour, Heure, Code, Module, Niveau, Salle, Surveillant       ║
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
# PROFESSIONAL COLOR PALETTE (University Style)
# ═══════════════════════════════════════════════════════════════════════════════
HEADER_RED = colors.HexColor('#7B2D26')       # Bordeaux header
HEADER_DARK = colors.HexColor('#5A1F1A')      # Darker red
BG_CREAM = colors.HexColor('#F5F0E6')         # Crème background
BG_LIGHT = colors.HexColor('#FEFDFB')         # White-cream
TEXT_DARK = colors.HexColor('#2D2D2D')        # Dark text
TEXT_GRAY = colors.HexColor('#666666')        # Gray text
BORDER_LIGHT = colors.HexColor('#D4C4A8')     # Light brown border
ROW_ALT = colors.HexColor('#F9F6F0')          # Alternating row

# App colors for accent
PRIMARY = colors.HexColor('#6366F1')
ACCENT = colors.HexColor('#8B5CF6')
SECONDARY = colors.HexColor('#EC4899')


def create_styles():
    """Crée les styles de texte professionnels"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='UnivTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=HEADER_RED,
        alignment=TA_CENTER,
        spaceAfter=3,
        fontName='Times-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=15,
        fontName='Times-Roman'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HEADER_RED,
        alignment=TA_CENTER,
        fontName='Times-Bold',
        spaceBefore=10,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='InfoText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        fontName='Times-Roman'
    ))
    
    styles.add(ParagraphStyle(
        name='InstructionTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HEADER_RED,
        alignment=TA_LEFT,
        fontName='Times-Bold',
        spaceBefore=15
    ))
    
    styles.add(ParagraphStyle(
        name='Instruction',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        fontName='Times-Roman',
        bulletIndent=15,
        leftIndent=25
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=TEXT_GRAY,
        alignment=TA_CENTER
    ))
    
    return styles


def format_date(date_obj):
    """Formate la date"""
    if date_obj:
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%d %b %Y')
        return str(date_obj)
    return ""


def get_day_name(date_obj):
    """Retourne le nom du jour"""
    days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    if date_obj and hasattr(date_obj, 'weekday'):
        return days_fr[date_obj.weekday()]
    return ""


def format_time(heure_debut, heure_fin=None):
    """Formate l'heure"""
    if heure_debut:
        start = str(heure_debut)[:5]
        if heure_fin:
            end = str(heure_fin)[:5]
            return f"{start} – {end}"
        return start
    return ""


def create_header_table(title, subtitle_parts, width=17*cm):
    """
    Crée l'en-tête professionnel du document avec logo si disponible
    subtitle_parts: liste de tuples (label, valeur) ou liste de strings
    """
    elements = []
    styles = create_styles()
    
    # Essayer de charger le logo
    logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'logo_univ.jpg')
    logo_exists = os.path.exists(logo_path)
    
    if logo_exists:
        # Header avec logos (gauche et droite)
        try:
            logo = Image(logo_path, width=2*cm, height=2*cm)
            header_data = [[logo, Paragraph(title, styles['UnivTitle']), logo]]
            header_table = Table(header_data, colWidths=[2.5*cm, 12*cm, 2.5*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)
        except:
            # Si erreur avec logo, juste le titre
            elements.append(Paragraph(title, styles['UnivTitle']))
    else:
        # Titre principal sans logo
        elements.append(Paragraph(title, styles['UnivTitle']))
    
    # Sous-titre avec séparateurs
    if subtitle_parts:
        if isinstance(subtitle_parts[0], tuple):
            subtitle_text = "  |  ".join([f"{label}: {val}" for label, val in subtitle_parts])
        else:
            subtitle_text = "  |  ".join(subtitle_parts)
        elements.append(Paragraph(subtitle_text, styles['SubTitle']))
    
    return elements


def create_section_title(text, width=17*cm):
    """Crée un titre de section avec décoration"""
    data = [[f"· {text} ·"]]
    table = Table(data, colWidths=[width])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), HEADER_RED),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table


def create_exam_table(headers, data, col_widths):
    """
    Crée un tableau d'examens avec le style universitaire
    Headers: Liste des en-têtes
    Data: Liste de listes (lignes)
    """
    table_data = [headers] + data
    
    table = Table(table_data, colWidths=col_widths)
    
    style_commands = [
        # Header style - burgundy background
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_RED),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Body style
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, HEADER_RED),
    ]
    
    # Alternating row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), ROW_ALT))
        else:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), BG_LIGHT))
    
    table.setStyle(TableStyle(style_commands))
    return table


def create_instructions_section():
    """Crée la section des instructions académiques"""
    styles = create_styles()
    elements = []
    
    # Ligne de séparation
    sep_line = Table([[""]], colWidths=[17*cm])
    sep_line.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, BORDER_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(sep_line)
    
    # Titre
    elements.append(Paragraph("· Academic Instructions ·", styles['InstructionTitle']))
    elements.append(Spacer(1, 8))
    
    # Instructions
    instructions = [
        "• Les étudiants doivent arriver 30 minutes avant l'heure de l'examen.",
        "• La carte d'étudiant valide est obligatoire.",
        "• Les appareils électroniques sont strictement interdits sauf autorisation.",
        "• L'entrée est interdite après 30 minutes du début de l'examen."
    ]
    
    for instr in instructions:
        elements.append(Paragraph(instr, styles['Instruction']))
        elements.append(Spacer(1, 3))
    
    return elements


def create_footer_text():
    """Crée le pied de page"""
    return Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} • Université de Boumerdes • ExamPro",
        ParagraphStyle('Footer', fontSize=8, textColor=TEXT_GRAY, alignment=TA_CENTER)
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PDF GENERATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_formation_schedule_pdf(formation_name, groupe, niveau, departement, examens):
    """
    Génère un PDF du planning étudiant - DESIGN UNIVERSITAIRE
    Colonnes: Date, Jour, Heure, Code, Module, Niveau, Salle, Surveillant
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = create_styles()
    elements = []
    
    # Header
    elements.extend(create_header_table(
        "University Final Examination Schedule",
        [
            ("Academic Year", "2025 – 2026"),
            ("Semester", "Fall"),
            ("Faculty", "Sciences"),
            ("Department", departement or "—")
        ]
    ))
    
    # Ligne décorative
    line = Table([[""]], colWidths=[17*cm])
    line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, BORDER_LIGHT)]))
    elements.append(line)
    elements.append(Spacer(1, 10))
    
    # Section titre
    elements.append(create_section_title("Examination Timetable"))
    
    # Info formation
    info_text = f"<b>Formation:</b> {formation_name}  |  <b>Groupe:</b> {groupe}  |  <b>Niveau:</b> {niveau}"
    elements.append(Paragraph(info_text, styles['InfoText']))
    elements.append(Spacer(1, 10))
    
    # Tableau des examens
    if examens:
        headers = ['Date', 'Day', 'Time', 'Course Code', 'Course Title', 'Level', 'Room', 'Invigilator']
        data = []
        
        for exam in examens:
            date_str = format_date(exam.get('date'))
            day = get_day_name(exam.get('date'))
            time = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
            code = exam.get('module_code', '')
            title = exam.get('module_nom', '')
            level = exam.get('niveau', niveau)
            room = exam.get('salle', '')
            invigilator = exam.get('surveillant', exam.get('prof_nom', ''))
            
            data.append([date_str, day, time, code, title, level, room, invigilator])
        
        col_widths = [2.2*cm, 2*cm, 2.2*cm, 2*cm, 4*cm, 1.5*cm, 1.5*cm, 2.2*cm]
        table = create_exam_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun examen planifié pour cette formation.", styles['InfoText']))
    
    # Instructions
    elements.extend(create_instructions_section())
    
    # Footer
    elements.append(Spacer(1, 20))
    elements.append(create_footer_text())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_professor_schedule_pdf(prof_nom, prof_prenom, departement, surveillances, matricule="", specialite=""):
    """
    Génère un PDF du planning de surveillance - DESIGN UNIVERSITAIRE
    Avec: Spécialité surveillée, Groupe, Département du groupe
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = create_styles()
    elements = []
    
    # Header
    elements.extend(create_header_table(
        "Examination Supervision Schedule",
        [
            ("Academic Year", "2025 – 2026"),
            ("Semester", "Fall"),
            ("Session", "Normal")
        ]
    ))
    
    # Ligne décorative
    line = Table([[""]], colWidths=[17*cm])
    line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, BORDER_LIGHT)]))
    elements.append(line)
    elements.append(Spacer(1, 10))
    
    # Section titre
    elements.append(create_section_title("Supervision Timetable"))
    
    # Info professeur
    info_parts = [f"<b>Professor:</b> {prof_prenom} {prof_nom}"]
    if matricule:
        info_parts.append(f"<b>ID:</b> {matricule}")
    info_parts.append(f"<b>Department:</b> {departement}")
    info_text = "  |  ".join(info_parts)
    elements.append(Paragraph(info_text, styles['InfoText']))
    if specialite:
        elements.append(Paragraph(f"<b>Specialization:</b> {specialite}", styles['InfoText']))
    elements.append(Spacer(1, 10))
    
    # Tableau des surveillances
    if surveillances:
        headers = ['Date', 'Time', 'Module', 'Formation', 'Group', 'Dept', 'Room', 'Role']
        data = []
        
        for surv in surveillances:
            date_str = format_date(surv.get('date'))
            time = format_time(surv.get('heure_debut'), surv.get('heure_fin'))
            module = surv.get('module_nom', surv.get('module_code', ''))
            formation = surv.get('formation', '')
            groupe = surv.get('groupe', '')
            dept = surv.get('departement', surv.get('dept', ''))
            room = surv.get('salle', '')
            role = surv.get('role', 'Surveillant')
            
            data.append([date_str, time, module, formation, groupe, dept, room, role])
        
        col_widths = [2*cm, 2*cm, 3*cm, 3*cm, 1.5*cm, 2*cm, 1.5*cm, 2*cm]
        table = create_exam_table(headers, data, col_widths)
        elements.append(table)
        
        # Statistiques
        elements.append(Spacer(1, 10))
        nb_resp = sum(1 for s in surveillances if 'RESP' in str(s.get('role', '')).upper())
        elements.append(Paragraph(
            f"<b>Total: {len(surveillances)} surveillances</b> ({nb_resp} as Chief, {len(surveillances)-nb_resp} as Assistant)",
            styles['InfoText']
        ))
    else:
        elements.append(Paragraph("Aucune surveillance assignée.", styles['InfoText']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(create_footer_text())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_room_schedule_pdf(salle_nom, salle_code, capacite, examens, salle_type="", batiment=""):
    """
    Génère un PDF du planning d'une salle - DESIGN UNIVERSITAIRE
    Avec: Prof surveillant, Groupe, Formation
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = create_styles()
    elements = []
    
    # Header
    elements.extend(create_header_table(
        "Examination Room Schedule",
        [
            ("Academic Year", "2025 – 2026"),
            ("Semester", "Fall"),
            ("Session", "Normal")
        ]
    ))
    
    # Ligne
    line = Table([[""]], colWidths=[17*cm])
    line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, BORDER_LIGHT)]))
    elements.append(line)
    elements.append(Spacer(1, 10))
    
    # Section titre
    elements.append(create_section_title("Room Occupation Schedule"))
    
    # Info salle
    info_parts = [f"<b>Room:</b> {salle_nom} ({salle_code})"]
    if salle_type:
        info_parts.append(f"<b>Type:</b> {salle_type}")
    info_parts.append(f"<b>Capacity:</b> {capacite} seats")
    info_text = "  |  ".join(info_parts)
    elements.append(Paragraph(info_text, styles['InfoText']))
    if batiment:
        elements.append(Paragraph(f"<b>Building:</b> {batiment}", styles['InfoText']))
    elements.append(Spacer(1, 10))
    
    # Tableau
    if examens:
        headers = ['Date', 'Time', 'Module', 'Formation', 'Group', 'Invigilator', 'Students']
        data = []
        
        for exam in examens:
            date_str = format_date(exam.get('date'))
            time = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
            module = exam.get('module_nom', exam.get('module_code', ''))
            formation = exam.get('formation', '')
            groupe = exam.get('groupe', '')
            prof = exam.get('surveillant', exam.get('prof_nom', ''))
            nb_etudiants = exam.get('nb_etudiants', '—')
            
            data.append([date_str, time, module, formation, groupe, prof, str(nb_etudiants)])
        
        col_widths = [2.2*cm, 2*cm, 3*cm, 3.5*cm, 1.5*cm, 3*cm, 1.8*cm]
        table = create_exam_table(headers, data, col_widths)
        elements.append(table)
        
        # Stats
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Total: {len(examens)} examinations scheduled</b>", styles['InfoText']))
    else:
        elements.append(Paragraph("No examinations scheduled for this room.", styles['InfoText']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(create_footer_text())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_department_schedule_pdf(dept_name, formations_data):
    """
    Génère un PDF complet pour un département - DESIGN UNIVERSITAIRE
    Une page par groupe avec toutes les infos
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = create_styles()
    elements = []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE DE GARDE
    # ═══════════════════════════════════════════════════════════════════════════
    elements.append(Spacer(1, 60))
    
    # Titre principal
    elements.append(Paragraph("University Final Examination Schedule", styles['UnivTitle']))
    elements.append(Spacer(1, 15))
    
    # Sous-titre
    elements.append(Paragraph(
        "Academic Year: 2025 – 2026  |  Semester: Fall  |  Faculty: Sciences",
        styles['SubTitle']
    ))
    
    # Ligne décorative
    line_table = Table([["", "", ""]], colWidths=[5.7*cm, 5.7*cm, 5.7*cm], rowHeights=[3*mm])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), HEADER_RED),
        ('BACKGROUND', (1, 0), (1, 0), HEADER_DARK),
        ('BACKGROUND', (2, 0), (2, 0), HEADER_RED),
    ]))
    elements.append(Spacer(1, 20))
    elements.append(line_table)
    elements.append(Spacer(1, 30))
    
    # Info département
    dept_title = Table([[f"Department: {dept_name}"]], colWidths=[14*cm])
    dept_title.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_CREAM),
        ('TEXTCOLOR', (0, 0), (-1, -1), HEADER_RED),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 18),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_LIGHT),
    ]))
    elements.append(dept_title)
    elements.append(Spacer(1, 30))
    
    # Liste des formations
    elements.append(Paragraph("<b>Formations included:</b>", styles['InfoText']))
    elements.append(Spacer(1, 10))
    
    for i, (form_name, data) in enumerate(formations_data.items(), 1):
        niveau = data.get('niveau', '')
        nb_exams = len(data.get('exams', []))
        elements.append(Paragraph(f"    {i}. {form_name} ({niveau}) - {nb_exams} exams", styles['InfoText']))
    
    elements.append(Spacer(1, 40))
    elements.append(create_footer_text())
    elements.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PAGES PAR FORMATION/GROUPE
    # ═══════════════════════════════════════════════════════════════════════════
    for formation_name, data in formations_data.items():
        niveau = data.get('niveau', '')
        examens = data.get('exams', [])
        
        if not examens:
            continue
        
        # Grouper par groupe
        exams_by_group = {}
        for exam in examens:
            grp = exam.get('groupe', 'G01')
            if grp not in exams_by_group:
                exams_by_group[grp] = []
            exams_by_group[grp].append(exam)
        
        for groupe in sorted(exams_by_group.keys()):
            group_exams = exams_by_group[groupe]
            
            # Header
            elements.extend(create_header_table(
                "University Final Examination Schedule",
                [
                    ("Academic Year", "2025 – 2026"),
                    ("Semester", "Fall"),
                    ("Department", dept_name)
                ]
            ))
            
            # Ligne
            line = Table([[""]], colWidths=[17*cm])
            line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, BORDER_LIGHT)]))
            elements.append(line)
            elements.append(Spacer(1, 5))
            
            # Titre section
            elements.append(create_section_title("Examination Timetable"))
            
            # Info
            elements.append(Paragraph(
                f"<b>Formation:</b> {formation_name}  |  <b>Level:</b> {niveau}  |  <b>Group:</b> {groupe}",
                styles['InfoText']
            ))
            elements.append(Spacer(1, 10))
            
            # Tableau
            headers = ['Date', 'Day', 'Time', 'Code', 'Module', 'Room', 'Invigilator']
            data_rows = []
            
            for exam in group_exams:
                date_str = format_date(exam.get('date'))
                day = get_day_name(exam.get('date'))
                time = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
                code = exam.get('module_code', '')
                title = exam.get('module_nom', '')
                room = exam.get('salle', '')
                invig = exam.get('surveillant', exam.get('prof_nom', ''))
                
                data_rows.append([date_str, day, time, code, title, room, invig])
            
            col_widths = [2.3*cm, 2*cm, 2.3*cm, 1.8*cm, 4.5*cm, 2*cm, 2.1*cm]
            table = create_exam_table(headers, data_rows, col_widths)
            elements.append(table)
            
            # Instructions
            elements.extend(create_instructions_section())
            
            # Footer
            elements.append(Spacer(1, 15))
            elements.append(create_footer_text())
            elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES for backward compatibility
# ═══════════════════════════════════════════════════════════════════════════════

def generate_student_schedule_pdf(formation_name, groupe, niveau, examens, departement=""):
    """Alias pour compatibilité"""
    return generate_formation_schedule_pdf(formation_name, groupe, niveau, departement, examens)


def generate_multi_group_pdf(formation_name, niveau, exams_by_group, departement=""):
    """Génère un PDF multi-groupes"""
    formations_data = {formation_name: {'niveau': niveau, 'exams': []}}
    for groupe, exams in exams_by_group.items():
        for exam in exams:
            exam['groupe'] = groupe
            formations_data[formation_name]['exams'].append(exam)
    return generate_department_schedule_pdf(departement or "Department", formations_data)


def generate_department_pdf(dept_name, formations_data):
    """Alias pour compatibilité"""
    return generate_department_schedule_pdf(dept_name, formations_data)
