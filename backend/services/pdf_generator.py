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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
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
        backColor=colors.HexColor('#004E89')
    ))
    
    styles.add(ParagraphStyle(
        name='SubInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT
    ))
    
    return styles


def generate_student_schedule_pdf(formation_name, groupe, niveau, examens):
    """
    Génère un PDF du planning étudiant
    
    Args:
        formation_name: Nom de la formation (ex: "Génie Logiciel")
        groupe: Groupe (ex: "GL01-GL02")
        niveau: Niveau (ex: "M1")
        examens: Liste de dict avec date, heure, module, salle
    
    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête université
    elements.append(Paragraph("🎓 Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Titre du planning
    elements.append(Paragraph("PLANNING DES EXAMENS DE SEMESTRE - S1", styles['ScheduleTitle']))
    elements.append(Spacer(1, 10))
    
    # Informations formation
    elements.append(Paragraph(f"<b>Formation:</b> {formation_name} | <b>Niveau:</b> {niveau} | <b>Groupe:</b> {groupe}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Année Universitaire:</b> 2025/2026", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Tableau des examens
    if examens:
        table_data = [['Date', 'Heure', 'Module', 'Salle']]
        for exam in examens:
            table_data.append([
                str(exam.get('date', '')),
                str(exam.get('heure', '')),
                str(exam.get('module', '')),
                str(exam.get('salle', ''))
            ])
        
        table = Table(table_data, colWidths=[4*cm, 3*cm, 6*cm, 3*cm])
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004E89')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            
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
    
    Args:
        prof_nom, prof_prenom: Nom du professeur
        departement: Département
        surveillances: Liste de dict avec date, heure, module, salle, role
    
    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête
    elements.append(Paragraph("🎓 Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Titre
    elements.append(Paragraph("PLANNING DE SURVEILLANCE - SESSION S1", styles['ScheduleTitle']))
    elements.append(Spacer(1, 10))
    
    # Info professeur
    elements.append(Paragraph(f"<b>Professeur:</b> {prof_prenom} {prof_nom}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Département:</b> {departement}", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Année Universitaire:</b> 2025/2026", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Tableau
    if surveillances:
        table_data = [['Date', 'Heure', 'Module', 'Salle', 'Rôle']]
        for surv in surveillances:
            table_data.append([
                str(surv.get('date', '')),
                str(surv.get('heure', '')),
                str(surv.get('module', '')),
                str(surv.get('salle', '')),
                str(surv.get('role', 'Surveillant'))
            ])
        
        table = Table(table_data, colWidths=[3*cm, 2.5*cm, 5*cm, 2.5*cm, 3*cm])
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
        ]))
        elements.append(table)
        
        # Résumé
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total surveillances:</b> {len(surveillances)}", styles['SubInfo']))
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
    
    Args:
        salle_nom: Nom de la salle
        salle_code: Code (ex: AMP10)
        capacite: Capacité de la salle
        examens: Liste de dict avec date, heure, module, formation, surveillant
    
    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête
    elements.append(Paragraph("🎓 Université M'Hamed Bougara", styles['UnivTitle']))
    elements.append(Paragraph("Faculté des Sciences", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Titre
    elements.append(Paragraph("PLANNING D'OCCUPATION - SESSION S1", styles['ScheduleTitle']))
    elements.append(Spacer(1, 10))
    
    # Info salle
    elements.append(Paragraph(f"<b>Salle:</b> {salle_nom} ({salle_code})", styles['SubInfo']))
    elements.append(Paragraph(f"<b>Capacité:</b> {capacite} places", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Tableau
    if examens:
        table_data = [['Date', 'Heure', 'Module', 'Formation']]
        for exam in examens:
            table_data.append([
                str(exam.get('date', '')),
                str(exam.get('heure', '')),
                str(exam.get('module', '')),
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
        ]))
        elements.append(table)
        
        # Résumé
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total examens:</b> {len(examens)}", styles['SubInfo']))
    else:
        elements.append(Paragraph("Aucun examen planifié dans cette salle", styles['Normal']))
    
    # Pied de page
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_master_schedule_pdf(formation_code, formation_name, groupes_data):
    """
    Génère un PDF du planning master comme dans la capture d'écran
    Format tableau avec jours en colonnes et groupes en lignes
    
    Args:
        formation_code: Code (ex: "M GL-S1")
        formation_name: Nom complet
        groupes_data: Dict avec {groupe: {date: {module, salle}}}
    
    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = create_header_style()
    elements = []
    
    # En-tête
    elements.append(Paragraph("Université M'Hamed Bougara - Faculté des Sciences", styles['UnivTitle']))
    elements.append(Paragraph(f"PLANNING DES EXAMENS DE SEMESTRE - S1", styles['Normal']))
    elements.append(Paragraph(f"<b>{formation_code}</b> - Année Universitaire: 2025/2026", styles['SubInfo']))
    elements.append(Spacer(1, 15))
    
    # Créer le tableau style planning
    if groupes_data:
        # Récupérer toutes les dates uniques
        all_dates = set()
        for groupe_info in groupes_data.values():
            all_dates.update(groupe_info.keys())
        sorted_dates = sorted(all_dates)
        
        # En-tête du tableau
        header = ['GROUPES'] + [str(d) for d in sorted_dates]
        table_data = [header]
        
        # Ligne pour l'heure
        heure_row = ['Séance'] + ['13:45:00'] * len(sorted_dates)
        table_data.append(heure_row)
        
        # Ligne pour les modules
        for groupe, modules in groupes_data.items():
            module_row = [f"Matière ({groupe})"]
            for date in sorted_dates:
                if date in modules:
                    module_row.append(modules[date].get('module', ''))
                else:
                    module_row.append('')
            table_data.append(module_row)
            
            # Ligne pour les salles
            salle_row = [groupe]
            for date in sorted_dates:
                if date in modules:
                    salle_row.append(modules[date].get('salle', ''))
                else:
                    salle_row.append('')
            table_data.append(salle_row)
        
        col_width = 2.2*cm
        table = Table(table_data, colWidths=[3*cm] + [col_width] * len(sorted_dates))
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFA500')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#FFFFCC')),
        ]))
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
