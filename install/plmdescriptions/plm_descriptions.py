# -*- encoding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 2010 OmniaSolutions (<http://omniasolutions.eu>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
from types import *

# Customized Automation to standardize and normalize descriptions and characteristics.
# It will allow to insert unit of measure (or label) and values, so to allow search on parts
# and it will build standardized description and labels and values to compose part description.

class plm_description(osv.osv):
    _name = "plm.description"
    _description = "PLM Descriptions"
    _columns = {
                'name': fields.char('Standard Description', size=128, required=True, translate=True),
                'description': fields.char('Note to Description', size=128, translate=True),
                'description_en': fields.char('Description English', size=128, translate=True),
                'umc1': fields.char('UM Characteristic 1', size=32,  help="Allow to specify a unit measure or a label for the characteristic"),
                'fmt1': fields.char('Format Characteristic 1', size=32, help="Allow to represent the measure: %s%s allow to build um and value, %s build only value, none build only value."),
                'umc2': fields.char('UM Characteristic 2', size=32, help="Allow to specify a unit measure or a label for the characteristic"),
                'fmt2': fields.char('Format Characteristic 2', size=32, help="Allow to represent the measure: %s%s allow to build um and value, %s build only value, none build only value."),
                'umc3': fields.char('UM Characteristic 3', size=32, help="Allow to specify a unit measure or a label for the characteristic"),
                'fmt3': fields.char('Format Characteristic 3', size=32, help="Allow to represent the measure: %s%s allow to build um and value, %s build only value, none build only value."),
                'fmtend': fields.char('Format Characteristic Composed', size=32, help="Allow to represent a normalized composition of technical characteristics : %s%s allow to build values."),
                'unitab': fields.char('Normative Rule', size=32, help="Specify normative rule (UNI, ISO, DIN...). It will be queued to build part description"),
                'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of product categories."),
    }
    _defaults = {
        'fmt1': lambda *a: False,
        'fmt2': lambda *a: False,
        'fmt3': lambda *a: False,
        'fmtend': lambda *a: False,
        'unitab': lambda *a: False,
    }
#    _sql_constraints = [
#        ('name_uniq', 'unique(name)', 'Standard Description has to be unique !'),
#    ]
#    Meanings and usage:
#    umc    : field containing a string to express unit of measure of a characteristic.
#    fmt    : field describing composition of umc with its value (when inserted in plm.compoent form)
#    fmtend : field describing composition of umcs to compose a normalized description.
#
#    Sample :
#
#name,description,description_en,umc1,fmt1,umc2,fmt2,fmtend
#ALBERO , Albero liscio , SHAFT , d. , %s %s , Lungh. , %s %s , %s x %s , 
#VITE UNI 5739 , Vite testa esagona interamente filettata , , M , %s%s , L. , %s , %sx%s , UNI 5739
#
# They will be composed like :
#    ALBERO d. 10 x L. 200
#    VITE M10x55 UNI 5739


plm_description()

class plm_component(osv.osv):
    _inherit = 'product.product'
    _columns = {
                'std_description': fields.many2one('plm.description','Standard Description', required=False, change_default=True, help="Select standard description for current product"),
                'std_umc1': fields.char('UM Characteristic 1', size=32, help="Allow to specifiy a unit measure for the first charachteristic"),
                'std_value1': fields.float('Value 1', help="Assign value to the first characteristic."),
                'std_umc2': fields.char('UM Characteristic 2', size=32, help="Allow to specifiy a unit measure for the second charachteristic"),
                'std_value2': fields.float('Value 2', help="Assign value to the second characteristic."),
                'std_umc3': fields.char('UM Characteristic 3', size=32, help="Allow to specifiy a unit measure for the third charachteristic"),
                'std_value3': fields.float('Value 3', help="Assign value to the second characteristic."),
    }
    _defaults = {
        'std_description': lambda *a: False,
        'std_umc1': lambda *a: False,
        'std_value1': lambda *a: False,
        'std_umc2': lambda *a: False,
        'std_value2': lambda *a: False,
        'std_umc3': lambda *a: False,
        'std_value3': lambda *a: False,
    }
#   Internal methods
    def _packvalues(self,fmt,label=False,value=False,value2=False):
        """
            Pack a string formatting it like specified in fmt
            mixing both label and value or only label.
        """
        retvalue=''
        
        if value2:
            if (type(value2) is FloatType):
                svalue2="%g" %value2
            else:
                svalue2=value2
        else:
            svalue2=''
            
        if value:
            if (type(value) is FloatType):
                svalue="%g" %value
            else:
                svalue=value
            cnt=fmt.count('%s')
            if cnt == 3:
                retvalue = fmt %(label, svalue, svalue2)
            if cnt == 2:
                retvalue = fmt %(label, svalue)
            elif cnt == 1:
                retvalue = fmt %svalue
        return retvalue

##  Customized Automations
    def on_change_stddesc(self, cr, uid, id, std_description=False):
        values={'description':False,'std_umc1':False,'std_value1':False,'std_umc2':False,'std_value2':False,'std_umc3':False,'std_value3':False}
        if std_description:
            thisDescription=self.pool.get('plm.description')
            thisObject=thisDescription.browse(cr, uid, std_description)
            if thisObject.name:
                values['description']=thisObject.name
                if thisObject.umc1:
                    values['std_umc1']=thisObject.umc1
                if thisObject.umc2:
                    values['std_umc2']=thisObject.umc2
                if thisObject.umc3:
                    values['std_umc3']=thisObject.umc3
        return {'value': values}

    def on_change_stdvalue(self, cr, uid, id, std_description=False, std_umc1=False, std_value1=False,\
                           std_umc2=False, std_value2=False, std_umc3=False, std_value3=False):
        if std_description:
            description1=False
            description2=False
            description3=False
            thisDescription=self.pool.get('plm.description')
            thisObject=thisDescription.browse(cr, uid, std_description)
            if thisObject.name:
                description=thisObject.name
                if thisObject.fmtend:
                    if std_umc1 and std_value1:
                        description1=self._packvalues(thisObject.fmt1, std_umc1, std_value1)
                    if std_umc2 and std_value2:
                        description2=self._packvalues(thisObject.fmt2, std_umc2, std_value2)
                    if std_umc3 and std_value3:
                        description3=self._packvalues(thisObject.fmt3, std_umc3, std_value3)
                    description=description+" "+self._packvalues(thisObject.fmtend, description1, description2, description3)
                else:
                    if std_umc1 and std_value1:
                        description=description+" "+self._packvalues(thisObject.fmt1, std_umc1, std_value1)
                    if std_umc2 and std_value2:
                        description=description+" "+self._packvalues(thisObject.fmt2, std_umc2, std_value2)
                    if std_umc3 and std_value3:
                        description=description+" "+self._packvalues(thisObject.fmt3, std_umc3, std_value3)
                if thisObject.unitab:
                    description=description+" "+thisObject.unitab
                return {'value': {'description': description}}            
        return {}
##  Customized Automations
plm_component()

