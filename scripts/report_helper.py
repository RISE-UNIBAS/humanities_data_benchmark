import hashlib

TABLE_SCRIPTS = """<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>"""

TEST_STYLE = """<style>
    /* Square styles */
    .test-rectangle {
        display: inline-flex;
        height: 20px;
        border-radius: 3px;
        text-align: center;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: regular;
        color: white;
        padding: 0 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .test-square {
        display: inline-flex;
        width: 30px;
        height: 20px;
        border-radius: 3px;
        text-align: center;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }
    /* Inner table styles */
    .inner-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0;
        padding: 0;
    }
    .inner-table th, .inner-table td {
        padding: 4px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .inner-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
</style>"""

COLOR_PALETTE = [
    "#3498db", "#e74c3c", "#f1c40f", "#2ecc71", "#9b59b6", "#ff5733", "#1abc9c", "#d35400",
    "#2980b9", "#c0392b", "#27ae60", "#8e44ad", "#e67e22", "#16a085", "#f39c12", "#bdc3c7",
    "#7f8c8d", "#34495e", "#2c3e50", "#ffcc00", "#ff6699", "#6699ff", "#66cc99", "#ff9966",
    "#9966ff", "#33cccc", "#cc6699", "#ff3366", "#33ff66", "#ff6600", "#00ccff", "#9933ff",
    "#ff0099", "#ff5050", "#66ff33", "#ff3300", "#00ff99", "#ff99cc", "#3399ff", "#ff9933",
    "#00ffcc", "#ff6600", "#99ff33", "#6633ff", "#ff3399", "#ff0066", "#ffcc33", "#00ff66",
    "#339933", "#cc33ff", "#ccff00", "#ff33cc", "#ff3300", "#33ccff", "#0099ff", "#ff0033",
    "#66ffff", "#ff0099", "#ff9966", "#33ffcc", "#99ccff", "#ff6699", "#ff6600", "#6699ff"
]

def get_badge(label, value, color="brightgreen", r_to_g=None, href=None):

    if r_to_g and isinstance(r_to_g, tuple):
        # tuple[0] is the range start, tuple[1] is the range end
        # The color goes from red to green
        try:
            if r_to_g[0] <= float(value) <= r_to_g[1]:
                color = f"{'%02x' % int(255 * (r_to_g[1] - float(value)) / (r_to_g[1] - r_to_g[0]))}ff00"
        except ValueError:
            color = "red"

    value = str(value)
    value = value.replace("-", "--")

    shield_html = f'<img src="https://img.shields.io/badge/{label}-{value}-{color}" alt="{label}">'
    if href:
        shield_html = f'<a href="{href}">{shield_html}</a>'

    return shield_html


def get_square(label, href=None):
    color_index = int(hashlib.md5(label.encode()).hexdigest(), 16) % 64
    color = COLOR_PALETTE[color_index]
    if href:
        return f"<a href='{href}'><span class='test-square' style='background-color: {color};'>{label}</span></a>"
    return f"<span class='test-square' style='background-color: {color};'>{label}</span>"

def get_rectangle(label, href=None):
    color_index = int(hashlib.md5(label.encode()).hexdigest(), 16) % 64
    color = COLOR_PALETTE[color_index]
    if href:
        return f"<a href='{href}'><span class='test-rectangle' style='background-color: {color};'>{label}</span></a>"
    return f"<span class='test-rectangle' style='background-color: {color};'>{label}</span>"

def create_html_table(headers: list, data, table_id="data-table"):
    header_html = ""
    for header in headers:
        header_html += f'    <th>{header}</th>\n'

    body_html = ""
    for row in data:
        body_html += "<tr>\n"
        for cell in row:
            body_html += f'    <td>{cell}</td>\n'
        body_html += "</tr>\n"

    table_html = (f'<table id="{table_id}" class="display">\n'
                   '  <thead><tr>\n'
                  f'{header_html}\n'
                   '  </tr></thead>\n'
                   '  <tbody>\n'
                  f'{body_html}\n'
                   '  </tbody>\n'
                   '</table>\n')

    script_html = ""
    if table_id:
        script_html = ('<script>\n'
                       '  $(document).ready(function() {\n'
                      f"    $('#{table_id}').DataTable({{\n"
                       '      "paging": true,\n'
                       '      "searching": true,\n'
                       '      "ordering": true,\n'
                       '      "info": true,\n'
                       '      "lengthMenu": [[10, 20, -1], [10, 20, "All"]],\n'
                       '    });\n'
                       '  });\n'
                       '</script>\n')


    return TABLE_SCRIPTS + TEST_STYLE + "\n" + table_html + "\n" + script_html

