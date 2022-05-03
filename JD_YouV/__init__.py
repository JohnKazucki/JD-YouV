# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

bl_info = {
    "name" : "JD YouV",
    "author" : "João Desager",
    "description" : "UV toolkit",
    "blender" : (3, 1, 0),
    "version" : (0, 1, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


from . operators.yv_unfuck import JD_OT_UV_unfuck
from . yv_panel import YV_PT_DEV

classes = ( JD_OT_UV_unfuck,
            YV_PT_DEV,
            )

def register():

    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    
    for c in classes:
        bpy.utils.unregister_class(c)
