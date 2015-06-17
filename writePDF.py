from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from lxml import etree, objectify

# for tables
from reportlab.lib import colors
from reportlab.lib import pagesizes 
from reportlab.platypus import Table, TableStyle

# for paragraphy stypes
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import (
    black,
    purple,
    white,
    yellow
    )

land_letter = pagesizes.landscape(pagesizes.letter)

p_width = land_letter[0]
p_height = land_letter[1]

styles = getSampleStyleSheet()

title = 'Threat scan report'
page_footer = ''

out_para_file = './paraOut.pdf'
in_file = './data/testXML.xml'

with open(in_file, 'r') as f:
    in_data = f.read()
    f.close()

in_xml_object = objectify.fromstring(in_data)

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold', 16)
    canvas.drawCentredString(p_width / 2, p_height - 50, title)
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.3 * inch, 'Page %d %s' % (doc.page, page_footer))
    canvas.restoreState()

def stylesheet():
    styles = {
        'default': ParagraphStyle(
        'default',
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=1,
        bulletFontName='Times-Roman',
        bulletFontSize=10,
        bulletIndent=0,
        textColor=black,
        backColor=None,
        wordWrap=None,
        borderWidth=0,
        borderPadding=0,
        borderColor=None,
        borderRadius=None,
        allowWidows=1,
        allowOrphans=0,
        textTransform=None,  # 'uppercase' | 'lowercase' | None
        endDots=None,         
        splitLongWords=1
        )
    }

    styles['device_name'] = ParagraphStyle(
        'device_name',
        parent=styles['default'],
        leftIndent=10
        )

    styles['threat_name'] = ParagraphStyle(
        'threat_name',
        parent=styles['default'],
        leftIndent=20
        )

    styles['status'] = ParagraphStyle(
        'status',
        parent=styles['default'],
        leftIndent=20
        )
    styles['trace'] = ParagraphStyle(
        'trace',
        parent=styles['default'],
        firstLineIndent=-10,
        leftIndent=40
        )

    return styles

def build_flowables(stylesheet, xml_object):
    
    para_list = []
    default_style = stylesheet['default']
    device_name_style = stylesheet['device_name']
    threat_name_style = stylesheet['threat_name']
    status_style = stylesheet['status']
    trace_style = stylesheet['trace']

    client_name = xml_object.client_name.text
    p = Paragraph('Client name: %s' % client_name, default_style)
    para_list.append(p)

    for el in xml_object.client_name.iterchildren():
        device_name = el.text
        threat_name = el.threat.threat_name.text # 'No threat found' has no children
        
        p = Paragraph('Device name: %s' % device_name, device_name_style)
        para_list.append(p)
        

        if threat_name == 'No threats found':
            p = Paragraph(threat_name, threat_name_style)
            para_list.append(p)

        else:    
            p = Paragraph('Threat name: %s' % threat_name, threat_name_style)
            para_list.append(p)
            status = el.threat.status.text
            date = el.threat.date.text

            p = Paragraph('Status: %s on %s' % (status, date), status_style)
            para_list.append(p) 
            

            for i in el.threat.trace[0:]:
                p = Paragraph(i.text, trace_style)
                para_list.append(p)

    return para_list 

def build_pdf(filename, flowables):
    doc = SimpleDocTemplate(filename, leftMargin=35, rightMargin=35, topMargin=50, bottomMargin=50, pagesize=land_letter)
    doc.build(flowables, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

if __name__ == '__main__':
    #go_for_table()
    #go_for_para()
    build_pdf(out_para_file, build_flowables(stylesheet(), in_xml_object))
