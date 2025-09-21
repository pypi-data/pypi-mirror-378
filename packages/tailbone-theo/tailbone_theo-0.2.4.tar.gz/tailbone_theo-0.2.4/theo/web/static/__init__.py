# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Static assets
"""

from fanstatic import Library, Resource


# libcache
libcache = Library('theo_libcache', 'libcache')
bb_vue_js = Resource(libcache, 'vue.esm-browser-3.4.31.prod.js')
bb_oruga_js = Resource(libcache, 'oruga-0.8.12.js')
bb_oruga_bulma_js = Resource(libcache, 'oruga-bulma-0.3.0.js')
bb_oruga_bulma_css = Resource(libcache, 'oruga-bulma-0.3.0.css')
bb_fontawesome_svg_core_js = Resource(libcache, 'fontawesome-svg-core-6.5.2.js')
bb_free_solid_svg_icons_js = Resource(libcache, 'free-solid-svg-icons-6.5.2.js')
bb_vue_fontawesome_js = Resource(libcache, 'vue-fontawesome-3.0.6.index.es.js')


def includeme(config):
    config.include('tailbone.static')
    config.add_static_view('tailbone_theo', 'tailbone_theo.web:static', cache_max_age=3600)
