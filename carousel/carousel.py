import textwrap
import urllib
from lxml import etree
from xml.etree import ElementTree as ET

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

from .utils import load_resource, render_template

from StringIO import StringIO

class CarouselBlock(XBlock):
    """
    An XBlock providing a responsive images carousel
    """

    display_name = String(help="This name appears in horizontal navigation at the top of the page.", 
        default="Images-carousel", 
        scope=Scope.content
    )
    
    data = String(help="",  
       scope=Scope.content,
       default=textwrap.dedent("""
            <carousel>
              <img>https://s3.amazonaws.com/xblock/slider/Slide1.JPG</img>
              <img>https://s3.amazonaws.com/xblock/slider/Slide2.JPG</img>
              <img>https://s3.amazonaws.com/xblock/slider/Slide3.JPG</img>
              <video>http://www.youtube.com/watch?v=8cBIAwh4EjA</video>
              <doc>http://research.google.com/archive/bigtable-osdi06.pdf</doc>
            </carousel>
          """
    ))

    def student_view(self, context):
        """
        Lab view, displayed to the student
        """

	root = ET.fromstring(self.data)
        items = {}
        for child in root:
            if child.tag == 'doc': child.text = urllib.quote(child.text, '')
            items[child] = {'tag': child.tag, 'text': child.text}

        fragment = Fragment()

        context = {
            'items': items,
        }

        fragment.add_content(render_template('/templates/html/carousel.html', context))
        fragment.add_javascript(load_resource('public/js/jquery-ui-1.10.4.custom.js'))
        fragment.add_css(load_resource('public/css/responsive-carousel.css'))
        fragment.add_css(load_resource('public/css/responsive-carousel.slide.css'))
        fragment.add_javascript(load_resource('public/js/responsive-carousel.js'))
        fragment.add_css_url("https://vjs.zencdn.net/4.5.1/video-js.css")
        fragment.add_javascript_url("https://vjs.zencdn.net/4.5.1/video.js")
        fragment.add_javascript(load_resource('public/js/youtube.js'))
        fragment.add_javascript('function CarouselBlock(runtime, element) { console.log("ok..."); }')
        fragment.initialize_js('CarouselBlock')

        return fragment

    def studio_view(self, context):
        """
        Studio edit view
        """

        fragment = Fragment()
        fragment.add_content(render_template('templates/html/carousel_edit.html', {'self': self, }))
        fragment.add_javascript(load_resource('public/js/jquery-ui-1.10.4.custom.js'))
        fragment.add_javascript(load_resource('public/js/carousel_edit.js'))
        fragment.initialize_js('CarouselEditBlock')

        return fragment

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        self.display_name = submissions['display_name']
        xml_content = submissions['data']

        try:
            etree.parse(StringIO(xml_content))
            self.data = xml_content
        except etree.XMLSyntaxError as e:
            return {
                'result': 'error',
                'message': e.message
            }

        return {
            'result': 'success',
        }

    @staticmethod
    def workbench_scenarios():
            return [("carousel demo", "<carousel />")]