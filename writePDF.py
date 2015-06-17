from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from lxml import etree, objectify
# for tables
from reportlab.lib import colors
from reportlab.lib import pagesizes 
from reportlab.platypus import Table, TableStyle

land_letter = pagesizes.landscape(pagesizes.letter)

p_height = defaultPageSize[1]
p_width = defaultPageSize[0]

styles = getSampleStyleSheet()

title = 'Threat scan report'
pageinfo = 'DO NOT WANT'

out_file = './firstOut.pdf'
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
    canvas.drawString(inch, 0.75 * inch, 'Page %d %s' % (doc.page, pageinfo))
    canvas.restoreState()

def go_for_table():
    doc = SimpleDocTemplate(out_file, pagesize=land_letter)
    flowables_list = []
    
    my_text = create_text_list(in_xml_object)
    t = Table(my_text, 1.2 * inch, hAlign='LEFT', vAlign='TOP')
    #t.setStyle(TableStyle([alignment='LEFT'
    #    ]))

    flowables_list.append(t)

    doc.build(flowables_list)

def go_for_para():
    raw_input('Warning: This is going to over-write the out_file')
    doc = SimpleDocTemplate(out_file)
    
    story = [Spacer(1, 0.5 * inch)]
    style = styles['Normal']
    # Dumps everything into paragraphs
    my_text = create_text(in_xml_object)
    for row in my_text:
        p = Paragraph(row, style)
        story.append(p)

    story.append(Spacer(1, 0.2 * inch))

    doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

def create_text_list(xml_object):
    text_list = []
    client_name = xml_object.client_name.text
    text_list.append(['Client name:', client_name])

    for el in xml_object.client_name.iterchildren():
        device_name = el.text
        threat_name = el.threat.threat_name.text # 'No threat found' has no children
        text_list.append(['Device name:', device_name])
        text_list.append(['', 'Threat name:', threat_name])
        if threat_name != 'No threats found':
            status = el.threat.status.text
            date = el.threat.date.text
            text_list.append(['', 'Status:',  status, 'on', date])
            
            for i in el.threat.trace[0:]:
                text_list.append(['', i.text])
    
    return text_list 

def create_text(xml_object):
    text_list = []
    client_name = xml_object.client_name.text
    text_list.append('Client name: %s' % client_name)

    for el in xml_object.client_name.iterchildren():
        device_name = el.text
        threat_name = el.threat.threat_name.text # 'No threat found' has no children
        text_list.append('Device name: %s' % device_name)
        text_list.append('Threat name: %s' % threat_name)
        if threat_name != 'No threats found':
            status = el.threat.status.text
            date = el.threat.date.text
            text_list.append('Status: %s on %s' % (status, date))
            
            for i in el.threat.trace[0:]:
                text_list.append(i.text)
    
    my_string = '\n'.join(text_list)
    for row in text_list:
        print type(row), row

    return text_list 

if __name__ == '__main__':
    go_for_table()

