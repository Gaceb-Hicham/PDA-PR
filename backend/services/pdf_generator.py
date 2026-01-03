"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Générateur de PDF Premium                                        ║
║  Design assorti au thème du site web                                        ║
║  Couleurs: Violet (#6366F1), Rose (#EC4899), Sombre (#0F0F1A)               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF
from io import BytesIO
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM COLOR PALETTE (matching website)
# ═══════════════════════════════════════════════════════════════════════════════
PRIMARY = colors.HexColor('#6366F1')      # Violet
PRIMARY_DARK = colors.HexColor('#4F46E5')
SECONDARY = colors.HexColor('#EC4899')    # Rose
ACCENT = colors.HexColor('#8B5CF6')       # Purple
SUCCESS = colors.HexColor('#10B981')      # Green
WARNING = colors.HexColor('#F59E0B')      # Orange

BG_DARK = colors.HexColor('#0F0F1A')
BG_CARD = colors.HexColor('#1E1E32')
TEXT_PRIMARY = colors.HexColor('#F8FAFC')
TEXT_SECONDARY = colors.HexColor('#94A3B8')
TEXT_MUTED = colors.HexColor('#64748B')
BORDER = colors.HexColor('#2D2D4A')


def create_premium_styles():
    """Crée les styles de texte premium"""
    styles = getSampleStyleSheet()
    
    # Titre université - Gradient effect simulé
    styles.add(ParagraphStyle(
        name='UnivTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=3,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='InfoLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=TEXT_MUTED,
        alignment=TA_LEFT
    ))
    
    styles.add(ParagraphStyle(
        name='InfoValue',
        parent=styles['Normal'],
        fontSize=10,
        textColor=BG_DARK,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='StatValue',
        parent=styles['Normal'],
        fontSize=12,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    return styles


def format_time(heure_debut, heure_fin=None):
    """Formate l'heure pour l'affichage"""
    if heure_debut:
        start = str(heure_debut)[:5]
        if heure_fin:
            end = str(heure_fin)[:5]
            return f"{start} - {end}"
        return start
    return ""


def format_module(code, nom=None):
    """Formate le nom du module"""
    if nom:
        return f"{nom}" if not code else f"{nom} ({code})"
    return code or ""


def create_gradient_header(title, subtitle="", width=16*cm):
    """Crée un header avec effet gradient (simulé avec bandes de couleur)"""
    elements = []
    
    # Bande de gradient simulée (3 bandes de couleur)
    gradient_data = [["", "", ""]]
    gradient_table = Table(gradient_data, colWidths=[width/3, width/3, width/3], rowHeights=[3*mm])
    gradient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), PRIMARY),
        ('BACKGROUND', (1, 0), (1, 0), ACCENT),
        ('BACKGROUND', (2, 0), (2, 0), SECONDARY),
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.white),
    ]))
    elements.append(gradient_table)
    
    # Titre principal
    title_table = Table([[title]], colWidths=[width])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_DARK),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(title_table)
    
    if subtitle:
        sub_table = Table([[subtitle]], colWidths=[width])
        sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_CARD),
            ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_SECONDARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(sub_table)
    
    return elements


def create_info_card(info_list, width=16*cm):
    """Crée une carte d'informations stylisée"""
    data = []
    for label, value in info_list:
        data.append([f"{label}:", str(value)])
    
    table = Table(data, colWidths=[4*cm, width - 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (0, -1), TEXT_MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), BG_DARK),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('ROUNDEDCORNERS', [3, 3, 3, 3]),
    ]))
    return table


def create_premium_table(headers, data, col_widths, header_color=PRIMARY):
    """Crée un tableau avec style premium"""
    table_data = [headers] + data
    
    table = Table(table_data, colWidths=col_widths)
    
    style_commands = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('LINEBELOW', (0, 0), (-1, 0), 2, header_color),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0, -1), (-1, -1), 1, BORDER),
        
        # Left border accent
        ('LINEBEFORE', (0, 1), (0, -1), 3, header_color),
    ]
    
    # Alternating row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8FAFC')))
        else:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.white))
    
    table.setStyle(TableStyle(style_commands))
    return table


def create_stats_row(stats, width=16*cm):
    """Crée une rangée de statistiques"""
    n = len(stats)
    col_width = width / n
    
    data = [[]]
    for stat in stats:
        cell = f"{stat['icon']}\n{stat['value']}\n{stat['label']}"
        data[0].append(cell)
    
    table = Table(data, colWidths=[col_width] * n)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), BG_DARK),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
    ]))
    return table


def create_footer(text=""):
    """Crée un pied de page"""
    if not text:
        text = f"ExamPro • Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    return Paragraph(text, ParagraphStyle('Footer', fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER))


# ═══════════════════════════════════════════════════════════════════════════════
# PDF GENERATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_student_schedule_pdf(formation_name, groupe, niveau, examens):
    """
    Génère un PDF du planning étudiant - DESIGN PREMIUM
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    styles = create_premium_styles()
    elements = []
    
    # Logo/Header university
    elements.append(Paragraph("⚡ ExamPro", styles['UnivTitle']))
    elements.append(Paragraph("Université M'Hamed Bougara • Faculté des Sciences", styles['SubTitle']))
    elements.append(Spacer(1, 10))
    
    # Gradient header
    elements.extend(create_gradient_header(
        f"📅 PLANNING DES EXAMENS",
        f"{formation_name} • Groupe {groupe}"
    ))
    elements.append(Spacer(1, 15))
    
    # Info card
    info_card = create_info_card([
        ("Formation", formation_name),
        ("Niveau", niveau),
        ("Groupe", groupe),
        ("Année", "2025/2026"),
        ("Semestre", "S1")
    ])
    elements.append(info_card)
    elements.append(Spacer(1, 15))
    
    # Exam table
    if examens:
        headers = ['📅 Date', '🕐 Horaire', '📖 Module', '🏢 Salle']
        data = []
        for exam in examens:
            heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
            module = format_module(exam.get('module_code'), exam.get('module_nom'))
            data.append([
                str(exam.get('date', '')),
                heure,
                module,
                str(exam.get('salle', ''))
            ])
        
        table = create_premium_table(headers, data, [3*cm, 3*cm, 7*cm, 3*cm], PRIMARY)
        elements.append(table)
        
        # Stats
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"<b>📊 Total: {len(examens)} examens</b>", 
                                 ParagraphStyle('Stats', fontSize=10, textColor=PRIMARY, alignment=TA_LEFT)))
    else:
        elements.append(Paragraph("📋 Aucun examen planifié", styles['InfoLabel']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_professor_schedule_pdf(prof_nom, prof_prenom, departement, surveillances):
    """
    Génère un PDF du planning de surveillance - DESIGN PREMIUM
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    styles = create_premium_styles()
    elements = []
    
    # Header
    elements.append(Paragraph("⚡ ExamPro", styles['UnivTitle']))
    elements.append(Paragraph("Université M'Hamed Bougara • Faculté des Sciences", styles['SubTitle']))
    elements.append(Spacer(1, 10))
    
    # Gradient header (secondary color for professors)
    elements.extend(create_gradient_header(
        f"👨‍🏫 PLANNING DE SURVEILLANCE",
        f"Prof. {prof_prenom} {prof_nom}"
    ))
    elements.append(Spacer(1, 15))
    
    # Info card
    info_card = create_info_card([
        ("Professeur", f"{prof_prenom} {prof_nom}"),
        ("Département", departement),
        ("Année", "2025/2026"),
        ("Session", "S1 - Normale")
    ])
    elements.append(info_card)
    elements.append(Spacer(1, 15))
    
    # Table
    if surveillances:
        headers = ['📅 Date', '🕐 Horaire', '📖 Module', '🏢 Salle', '🎯 Rôle']
        data = []
        for surv in surveillances:
            heure = format_time(surv.get('heure_debut'), surv.get('heure_fin'))
            module = format_module(surv.get('module_code'), surv.get('module_nom'))
            data.append([
                str(surv.get('date', '')),
                heure,
                module,
                str(surv.get('salle', '')),
                str(surv.get('role', 'Surveillant'))
            ])
        
        table = create_premium_table(headers, data, [2.5*cm, 2.5*cm, 5*cm, 2.5*cm, 3*cm], ACCENT)
        elements.append(table)
        
        # Stats
        elements.append(Spacer(1, 15))
        nb_resp = sum(1 for s in surveillances if s.get('role') == 'RESPONSABLE')
        nb_surv = len(surveillances) - nb_resp
        elements.append(Paragraph(
            f"<b>📊 Total: {len(surveillances)} surveillances</b> • {nb_resp} responsable • {nb_surv} surveillant", 
            ParagraphStyle('Stats', fontSize=10, textColor=ACCENT, alignment=TA_LEFT)
        ))
    else:
        elements.append(Paragraph("📋 Aucune surveillance assignée", styles['InfoLabel']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_room_schedule_pdf(salle_nom, salle_code, capacite, examens):
    """
    Génère un PDF du planning d'une salle - DESIGN PREMIUM
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    styles = create_premium_styles()
    elements = []
    
    # Header
    elements.append(Paragraph("⚡ ExamPro", styles['UnivTitle']))
    elements.append(Paragraph("Université M'Hamed Bougara • Faculté des Sciences", styles['SubTitle']))
    elements.append(Spacer(1, 10))
    
    # Gradient header (success color for rooms)
    elements.extend(create_gradient_header(
        f"🏢 PLANNING D'OCCUPATION",
        f"Salle {salle_nom} ({salle_code})"
    ))
    elements.append(Spacer(1, 15))
    
    # Info card
    info_card = create_info_card([
        ("Salle", salle_nom),
        ("Code", salle_code),
        ("Capacité", f"{capacite} places"),
        ("Session", "S1 - 2025/2026")
    ])
    elements.append(info_card)
    elements.append(Spacer(1, 15))
    
    # Table
    if examens:
        headers = ['📅 Date', '🕐 Horaire', '📖 Module', '📚 Formation']
        data = []
        for exam in examens:
            heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
            module = format_module(exam.get('module_code'), exam.get('module_nom'))
            data.append([
                str(exam.get('date', '')),
                heure,
                module,
                str(exam.get('formation', ''))
            ])
        
        table = create_premium_table(headers, data, [3*cm, 3*cm, 5*cm, 5*cm], SUCCESS)
        elements.append(table)
        
        # Stats
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"<b>📊 Total: {len(examens)} examens planifiés</b>", 
                                 ParagraphStyle('Stats', fontSize=10, textColor=SUCCESS, alignment=TA_LEFT)))
    else:
        elements.append(Paragraph("📋 Aucun examen planifié", styles['InfoLabel']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_multi_group_pdf(formation_name, niveau, exams_by_group):
    """
    Génère un PDF multi-pages: une page par groupe - DESIGN PREMIUM
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    styles = create_premium_styles()
    elements = []
    
    for groupe, examens in exams_by_group.items():
        # Header
        elements.append(Paragraph("⚡ ExamPro", styles['UnivTitle']))
        elements.append(Paragraph("Université M'Hamed Bougara • Faculté des Sciences", styles['SubTitle']))
        elements.append(Spacer(1, 10))
        
        # Gradient header
        elements.extend(create_gradient_header(
            f"📅 PLANNING DES EXAMENS",
            f"{formation_name} • {groupe}"
        ))
        elements.append(Spacer(1, 15))
        
        # Info
        info_card = create_info_card([
            ("Formation", formation_name),
            ("Niveau", niveau),
            ("Groupe", groupe),
            ("Année", "2025/2026")
        ])
        elements.append(info_card)
        elements.append(Spacer(1, 15))
        
        # Table
        if examens:
            headers = ['📅 Date', '🕐 Horaire', '📖 Module', '🏢 Salle']
            data = []
            for exam in examens:
                heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
                module = format_module(exam.get('module_code'), exam.get('module_nom'))
                data.append([
                    str(exam.get('date', '')),
                    heure,
                    module,
                    str(exam.get('salle', ''))
                ])
            
            table = create_premium_table(headers, data, [3*cm, 3*cm, 7*cm, 3*cm], PRIMARY)
            elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(create_footer())
        elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_department_pdf(dept_name, formations_data):
    """
    Génère un PDF complet pour un département - DESIGN PREMIUM
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    styles = create_premium_styles()
    elements = []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE DE GARDE
    # ═══════════════════════════════════════════════════════════════════════════
    elements.append(Spacer(1, 80))
    elements.append(Paragraph("⚡ ExamPro", styles['UnivTitle']))
    elements.append(Paragraph("Plateforme de Gestion des Examens", styles['SubTitle']))
    elements.append(Spacer(1, 40))
    
    # Big title
    cover_title = Table([[f"📚 PLANNINGS DES EXAMENS"]], colWidths=[14*cm])
    cover_title.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_DARK),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(cover_title)
    elements.append(Spacer(1, 20))
    
    # Gradient bar
    grad_bar = Table([["", "", ""]], colWidths=[14*cm/3, 14*cm/3, 14*cm/3], rowHeights=[5*mm])
    grad_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), PRIMARY),
        ('BACKGROUND', (1, 0), (1, 0), ACCENT),
        ('BACKGROUND', (2, 0), (2, 0), SECONDARY),
    ]))
    elements.append(grad_bar)
    elements.append(Spacer(1, 30))
    
    # Department info
    dept_table = Table([
        ["🏛️ Département", dept_name],
        ["📅 Année Universitaire", "2025/2026"],
        ["📖 Semestre", "S1"],
        ["📚 Formations", str(len(formations_data))]
    ], colWidths=[5*cm, 9*cm])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (0, -1), TEXT_MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), BG_DARK),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
    ]))
    elements.append(dept_table)
    elements.append(Spacer(1, 30))
    
    # List of formations
    elements.append(Paragraph("<b>📋 Formations incluses:</b>", styles['InfoValue']))
    elements.append(Spacer(1, 10))
    for i, form_name in enumerate(formations_data.keys(), 1):
        elements.append(Paragraph(f"    {i}. {form_name}", styles['InfoLabel']))
    
    elements.append(Spacer(1, 50))
    elements.append(create_footer("Université M'Hamed Bougara • Faculté des Sciences • Boumerdès"))
    elements.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PAGES PAR FORMATION/GROUPE
    # ═══════════════════════════════════════════════════════════════════════════
    for formation_name, data in formations_data.items():
        niveau = data.get('niveau', '')
        examens = data.get('exams', [])
        
        if not examens:
            continue
        
        # Group exams by groupe
        exams_by_group = {}
        for exam in examens:
            groupe = exam.get('groupe', 'G01')
            if groupe not in exams_by_group:
                exams_by_group[groupe] = []
            exams_by_group[groupe].append(exam)
        
        for groupe in sorted(exams_by_group.keys()):
            group_exams = exams_by_group[groupe]
            
            # Header
            elements.append(Paragraph("⚡ ExamPro", styles['UnivTitle']))
            elements.append(Paragraph(f"{dept_name} • Session S1 2025/2026", styles['SubTitle']))
            elements.append(Spacer(1, 10))
            
            # Formation title
            form_title = Table([[f"📚 {formation_name}"]], colWidths=[16*cm])
            form_title.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(form_title)
            
            # Groupe subtitle
            grp_title = Table([[f"👥 GROUPE: {groupe}"]], colWidths=[16*cm])
            grp_title.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(grp_title)
            elements.append(Spacer(1, 15))
            
            # Info
            elements.append(Paragraph(f"<b>Niveau:</b> {niveau} • <b>Département:</b> {dept_name}", 
                                     ParagraphStyle('Info', fontSize=9, textColor=TEXT_MUTED)))
            elements.append(Spacer(1, 10))
            
            # Table
            headers = ['📅 Date', '🕐 Horaire', '📖 Module', '🏢 Salle']
            data_rows = []
            for exam in group_exams:
                heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
                module = format_module(exam.get('module_code'), exam.get('module_nom'))
                data_rows.append([
                    str(exam.get('date', '')),
                    heure,
                    module,
                    str(exam.get('salle', ''))
                ])
            
            table = create_premium_table(headers, data_rows, [3*cm, 3*cm, 6.5*cm, 3.5*cm], PRIMARY_DARK)
            elements.append(table)
            
            # Stats
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(f"📊 <b>{len(group_exams)} examens</b> pour ce groupe", 
                                     ParagraphStyle('Stats', fontSize=9, textColor=PRIMARY)))
            
            # Footer
            elements.append(Spacer(1, 30))
            elements.append(create_footer())
            elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
