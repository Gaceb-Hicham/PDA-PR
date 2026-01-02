"""
Génération de PDF pour les emplois du temps d'examens
- Planning étudiant par groupe
- Planning professeur (surveillances)
- Planning par salle
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


def create_header_style():
    """Crée les styles de texte"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='UnivTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#004E89'),
        alignment=TA_CENTER,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='ScheduleTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='SubInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT
    ))
    
    return styles


def format_time(heure_debut, heure_fin=None):
    """Formate l'heure pour l'affichage"""
    if heure_debut:
        start = str(heure_debut)[:5]  # HH:MM
        if heure_fin:
            end = str(heure_fin)[:5]
            return f"{start} - {end}"
        return start
    return ""


def format_module(code, nom=None):
    """Formate le nom du module - affiche Nom (Code) ou juste Nom"""
    if nom:
        return f"{nom} ({code})" if code else nom
    return code or ""


def generate_student_schedule_pdf(formation_name, groupe, niveau, examens):
    """
    Génère un PDF du planning étudiant
    
    Args:
        formation_name: Nom de la formation (ex: "Génie Logiciel")
        groupe: Groupe (ex: "GL01-GL02")
        niveau: Niveau (ex: "M1")
        examens: Liste de dict avec date, heure_debut, heure_fin, module_code, module_nom, salle
    
    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête université
    elements.append(Paragraph("Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Titre du planning
    title_table = Table([["PLANNING DES EXAMENS - SEMESTRE S1"]], colWidths=[16*cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#004E89')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 10))
    
    # Informations formation
    elements.append(Paragraph(f"<b>Formation:</b> {formation_name}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Niveau:</b> {niveau} | <b>Groupe:</b> {groupe}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Année Universitaire:</b> 2025/2026", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Tableau des examens
    if examens:
        table_data = [['Date', 'Horaire', 'Module', 'Salle']]
        for exam in examens:
            # Formater l'heure (début - fin)
            heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
            if not heure:
                heure = str(exam.get('heure', ''))[:5]
            
            # Formater le module (nom + code)
            module = format_module(exam.get('module_code', exam.get('module', '')), 
                                  exam.get('module_nom'))
            
            table_data.append([
                str(exam.get('date', '')),
                heure,
                module,
                str(exam.get('salle', ''))
            ])
        
        table = Table(table_data, colWidths=[3*cm, 3*cm, 7*cm, 3*cm])
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004E89')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Date et heure centrés
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Module à gauche
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Salle centré
            
            # Bordures
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            
            # Alternance couleurs
            *[('BACKGROUND', (0, i), (-1, i), colors.white) for i in range(2, len(table_data), 2)]
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun examen planifié", styles['Normal']))
    
    # Pied de page
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_professor_schedule_pdf(prof_nom, prof_prenom, departement, surveillances):
    """
    Génère un PDF du planning de surveillance d'un professeur
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête
    elements.append(Paragraph("Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Titre
    title_table = Table([["PLANNING DE SURVEILLANCE - SESSION S1"]], colWidths=[16*cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 10))
    
    # Info professeur
    elements.append(Paragraph(f"<b>Professeur:</b> {prof_prenom} {prof_nom}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Département:</b> {departement}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Année Universitaire:</b> 2025/2026", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Tableau
    if surveillances:
        table_data = [['Date', 'Horaire', 'Module', 'Salle', 'Rôle']]
        for surv in surveillances:
            heure = format_time(surv.get('heure_debut'), surv.get('heure_fin'))
            if not heure:
                heure = str(surv.get('heure', ''))[:5]
            
            module = format_module(surv.get('module_code', surv.get('module', '')),
                                  surv.get('module_nom'))
            
            table_data.append([
                str(surv.get('date', '')),
                heure,
                module,
                str(surv.get('salle', '')),
                str(surv.get('role', 'Surveillant'))
            ])
        
        table = Table(table_data, colWidths=[2.5*cm, 2.5*cm, 5.5*cm, 2.5*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Module à gauche
        ]))
        elements.append(table)
        
        # Résumé
        elements.append(Spacer(1, 20))
        nb_resp = sum(1 for s in surveillances if s.get('role') == 'RESPONSABLE')
        nb_surv = len(surveillances) - nb_resp
        elements.append(Paragraph(f"<b>Total:</b> {len(surveillances)} surveillances ({nb_resp} responsable, {nb_surv} surveillant)", 
                                 styles['SubInfo']))
    else:
        elements.append(Paragraph("Aucune surveillance assignée", styles['Normal']))
    
    # Pied de page
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_room_schedule_pdf(salle_nom, salle_code, capacite, examens):
    """
    Génère un PDF du planning d'une salle
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête
    elements.append(Paragraph("Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Titre
    title_table = Table([["PLANNING D'OCCUPATION - SESSION S1"]], colWidths=[16*cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 10))
    
    # Info salle
    elements.append(Paragraph(f"<b>Salle:</b> {salle_nom} ({salle_code})", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Capacité:</b> {capacite} places", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Tableau
    if examens:
        table_data = [['Date', 'Horaire', 'Module', 'Formation']]
        for exam in examens:
            heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
            if not heure:
                heure = str(exam.get('heure', ''))[:5]
            
            module = format_module(exam.get('module_code', exam.get('module', '')),
                                  exam.get('module_nom'))
            
            table_data.append([
                str(exam.get('date', '')),
                heure,
                module,
                str(exam.get('formation', ''))
            ])
        
        table = Table(table_data, colWidths=[3*cm, 3*cm, 5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F6F3')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (2, 1), (3, -1), 'LEFT'),  # Module et formation à gauche
        ]))
        elements.append(table)
        
        # Résumé
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total:</b> {len(examens)} examens planifiés", styles['SubInfo']))
    else:
        elements.append(Paragraph("Aucun examen planifié dans cette salle", styles['Normal']))
    
    # Pied de page
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_formation_master_pdf(formation_code, formation_name, niveau, groupes, examens_by_date):
    """
    Génère un PDF du planning master (style tableau par date avec groupes)
    Format: Colonnes = dates, Lignes = groupes avec leur salle
    
    Args:
        formation_code: ex "GL"
        formation_name: ex "Génie Logiciel"
        niveau: ex "M1"
        groupes: Liste des groupes ["GL01-GL02", "GL03-GL04", "GL05"]
        examens_by_date: Dict {date: {module, heure, salles: {groupe: salle}}}
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête
    elements.append(Paragraph("Université M'Hamed Bougara - Faculté des Sciences", styles['UnivTitle']))
    elements.append(Paragraph(f"PLANNING DES EXAMENS DE SEMESTRE - S1", styles['Normal']))
    elements.append(Paragraph(f"<b>{niveau} {formation_name}</b> - Année Universitaire: 2025/2026", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    if examens_by_date:
        # Créer le tableau
        dates = sorted(examens_by_date.keys())
        
        # En-tête: Groupes | Date1 | Date2 | ...
        header = ['GROUPES'] + [str(d) for d in dates]
        table_data = [header]
        
        # Ligne heure
        heure_row = ['Séance']
        for d in dates:
            exam = examens_by_date[d]
            heure_row.append(format_time(exam.get('heure_debut'), exam.get('heure_fin')))
        table_data.append(heure_row)
        
        # Ligne module
        module_row = ['Matière']
        for d in dates:
            exam = examens_by_date[d]
            module_row.append(format_module(exam.get('module_code'), exam.get('module_nom')))
        table_data.append(module_row)
        
        # Lignes par groupe
        for groupe in groupes:
            salle_row = [groupe]
            for d in dates:
                exam = examens_by_date[d]
                salles = exam.get('salles', {})
                salle_row.append(salles.get(groupe, ''))
            table_data.append(salle_row)
        
        col_width = min(2.5*cm, 24*cm / (len(dates) + 1))
        table = Table(table_data, colWidths=[3.5*cm] + [col_width] * len(dates))
        table.setStyle(TableStyle([
            # En-tête dates (orange)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFA500')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            # Colonne groupes (jaune clair)
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#FFFFCC')),
            # Lignes heure et matière
            ('BACKGROUND', (1, 1), (-1, 2), colors.HexColor('#FFF5E6')),
        ]))
        elements.append(table)
    
    # Pied de page
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_multi_group_pdf(formation_name, niveau, exams_by_group):
    """
    Génère un PDF multi-pages: une page par groupe
    
    Args:
        formation_name: Nom de la formation
        niveau: Niveau (L1, L2, M1, etc.)
        exams_by_group: Dict {groupe: [list of exams]}
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    for groupe, examens in exams_by_group.items():
        # En-tête université
        elements.append(Paragraph("Université M'Hamed Bougara", styles['UnivTitle']))
        elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Titre
        title_table = Table([[f"PLANNING DES EXAMENS - {groupe}"]], colWidths=[16*cm])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#004E89')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 10))
        
        # Info
        elements.append(Paragraph(f"<b>Formation:</b> {formation_name}", styles['SubInfo']))
        elements.append(Paragraph(f"<b>Niveau:</b> {niveau} | <b>Groupe:</b> {groupe}", styles['SubInfo']))
        elements.append(Paragraph(f"<b>Année Universitaire:</b> 2025/2026", styles['SubInfo']))
        elements.append(Spacer(1, 15))
        
        # Tableau
        if examens:
            table_data = [['Date', 'Horaire', 'Module', 'Salle']]
            for exam in examens:
                heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
                module = format_module(exam.get('module_code'), exam.get('module_nom'))
                table_data.append([
                    str(exam.get('date', '')),
                    heure,
                    module,
                    str(exam.get('salle', ''))
                ])
            
            table = Table(table_data, colWidths=[3*cm, 3*cm, 7*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004E89')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(table)
        
        # Pied de page
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                                 ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
        
        # Saut de page pour le groupe suivant
        from reportlab.platypus import PageBreak
        elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_department_pdf(dept_name, formations_data):
    """
    Génère un PDF pour tout un département: une page par formation/groupe
    Chaque groupe a sa propre section pour une lecture claire
    
    Args:
        dept_name: Nom du département
        formations_data: Dict {formation_name: {'niveau': str, 'exams': [list with groupe field]}}
    """
    from reportlab.platypus import PageBreak
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = create_header_style()
    elements = []
    
    # Page de garde
    elements.append(Spacer(1, 100))
    elements.append(Paragraph("Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 50))
    
    title_table = Table([[f"PLANNINGS DES EXAMENS"]], colWidths=[16*cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 18),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"<b>Département:</b> {dept_name}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Année Universitaire:</b> 2025/2026", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Semestre:</b> S1", styles['SubInfo']))
    elements.append(Spacer(1, 30))
    
    # Liste des formations
    elements.append(Paragraph("<b>Formations incluses:</b>", styles['SubInfo']))
    for i, form_name in enumerate(formations_data.keys(), 1):
        elements.append(Paragraph(f"  {i}. {form_name}", styles['Normal']))
    
    elements.append(PageBreak())
    
    # Pour chaque formation
    for formation_name, data in formations_data.items():
        niveau = data.get('niveau', '')
        examens = data.get('exams', [])
        
        if not examens:
            continue
        
        # Grouper les examens par groupe
        exams_by_group = {}
        for exam in examens:
            groupe = exam.get('groupe', 'G01')
            if groupe not in exams_by_group:
                exams_by_group[groupe] = []
            exams_by_group[groupe].append(exam)
        
        # Pour chaque groupe de cette formation
        for groupe in sorted(exams_by_group.keys()):
            group_exams = exams_by_group[groupe]
            
            # En-tête de page
            elements.append(Paragraph("Université M'Hamed Bougara - Faculté des Sciences", 
                                      ParagraphStyle('SmallHeader', fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
            elements.append(Spacer(1, 5))
            
            # Titre formation
            formation_title = Table([[f"{formation_name}"]], colWidths=[16*cm])
            formation_title.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#004E89')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(formation_title)
            elements.append(Spacer(1, 5))
            
            # Sous-titre groupe
            groupe_title = Table([[f"GROUPE: {groupe}"]], colWidths=[16*cm])
            groupe_title.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(groupe_title)
            elements.append(Spacer(1, 10))
            
            # Infos
            elements.append(Paragraph(f"<b>Niveau:</b> {niveau} | <b>Département:</b> {dept_name}", styles['SubInfo']))
            elements.append(Spacer(1, 10))
            
            # Tableau des examens
            table_data = [['Date', 'Horaire', 'Module', 'Salle']]
            for exam in group_exams:
                heure = format_time(exam.get('heure_debut'), exam.get('heure_fin'))
                module = format_module(exam.get('module_code'), exam.get('module_nom'))
                table_data.append([
                    str(exam.get('date', '')),
                    heure,
                    module,
                    str(exam.get('salle', ''))
                ])
            
            table = Table(table_data, colWidths=[3*cm, 3*cm, 6.5*cm, 3.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (0, 1), (1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                # Alternance de couleurs
                *[('BACKGROUND', (0, i), (-1, i), colors.white) for i in range(2, len(table_data), 2)]
            ]))
            elements.append(table)
            
            # Pied de section
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(f"Total: {len(group_exams)} examens", 
                                      ParagraphStyle('Total', fontSize=9, textColor=colors.grey)))
            
            # Décision intelligente: nouvelle page si plus de 8 examens ou si c'est le dernier groupe
            # Sinon, on peut mettre 2 petits tableaux sur une page
            if len(group_exams) > 8:
                elements.append(PageBreak())
            else:
                elements.append(Spacer(1, 30))
                # Vérifier si on a de la place pour le prochain
                elements.append(PageBreak())  # Pour l'instant, toujours nouvelle page pour clarté
    
    # Pied de page final
    elements.append(Paragraph(f"Département {dept_name} - Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

