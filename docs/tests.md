# Test Overview

This page provides an overview of all tests. Click on the test name to see the detailed results.

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script><style>
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
        width: 45px;
        height: 20px;
        border-radius: 3px;
        text-align: center;
        align-items: center;
        justify-content: center;
        font-size: 11px;
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
    
    /* Sortable table styles */
    .sortable-table th[onclick] {
        cursor: pointer;
        user-select: none;
        transition: background-color 0.2s;
    }
    .sortable-table th[onclick]:hover {
        background-color: #e8e8e8;
    }
    
    /* Rules column styles */
    .inner-table td:nth-child(6) {
        max-width: 200px;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Radar chart container styles */
    #performanceRadar {
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #fafafa;
    }
</style>
<table id="data-table" class="display">
  <thead><tr>
    <th>Test</th>
    <th>Name</th>
    <th>Provider</th>
    <th>Model</th>
    <th>Dataclass</th>
    <th>Temperature</th>
    <th>Role Description</th>
    <th>Prompt File</th>
    <th>Legacy Test</th>

  </tr></thead>
  <tbody>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0001'><span class='test-square' style='background-color: #ff0066;'>T0001</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0002'><span class='test-square' style='background-color: #ff3300;'>T0002</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0003'><span class='test-square' style='background-color: #ff33cc;'>T0003</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0004'><span class='test-square' style='background-color: #c0392b;'>T0004</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0005'><span class='test-square' style='background-color: #27ae60;'>T0005</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0006'><span class='test-square' style='background-color: #f39c12;'>T0006</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0008'><span class='test-square' style='background-color: #ffcc00;'>T0008</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0009'><span class='test-square' style='background-color: #f39c12;'>T0009</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0010'><span class='test-square' style='background-color: #99ff33;'>T0010</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0011'><span class='test-square' style='background-color: #33ccff;'>T0011</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0012'><span class='test-square' style='background-color: #ff6600;'>T0012</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0013'><span class='test-square' style='background-color: #0099ff;'>T0013</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0014'><span class='test-square' style='background-color: #7f8c8d;'>T0014</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0015'><span class='test-square' style='background-color: #cc33ff;'>T0015</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0016'><span class='test-square' style='background-color: #33ccff;'>T0016</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0017'><span class='test-square' style='background-color: #ff6600;'>T0017</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0018'><span class='test-square' style='background-color: #ff9966;'>T0018</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0019'><span class='test-square' style='background-color: #ff5733;'>T0019</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0020'><span class='test-square' style='background-color: #16a085;'>T0020</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0021'><span class='test-square' style='background-color: #ff3300;'>T0021</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0022'><span class='test-square' style='background-color: #99ff33;'>T0022</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0023'><span class='test-square' style='background-color: #33ffcc;'>T0023</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0024'><span class='test-square' style='background-color: #ff33cc;'>T0024</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0025'><span class='test-square' style='background-color: #33ff66;'>T0025</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0026'><span class='test-square' style='background-color: #6633ff;'>T0026</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0027'><span class='test-square' style='background-color: #ff9966;'>T0027</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0028'><span class='test-square' style='background-color: #ff33cc;'>T0028</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0029'><span class='test-square' style='background-color: #ff6699;'>T0029</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0030'><span class='test-square' style='background-color: #3399ff;'>T0030</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0031'><span class='test-square' style='background-color: #ff0099;'>T0031</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0032'><span class='test-square' style='background-color: #ff3366;'>T0032</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0033'><span class='test-square' style='background-color: #f39c12;'>T0033</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0034'><span class='test-square' style='background-color: #34495e;'>T0034</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0035'><span class='test-square' style='background-color: #6699ff;'>T0035</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0036'><span class='test-square' style='background-color: #ff6600;'>T0036</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0037'><span class='test-square' style='background-color: #ff6600;'>T0037</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0038'><span class='test-square' style='background-color: #ff9966;'>T0038</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0039'><span class='test-square' style='background-color: #66cc99;'>T0039</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0040'><span class='test-square' style='background-color: #34495e;'>T0040</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0041'><span class='test-square' style='background-color: #33ffcc;'>T0041</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0042'><span class='test-square' style='background-color: #c0392b;'>T0042</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0043'><span class='test-square' style='background-color: #00ffcc;'>T0043</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0044'><span class='test-square' style='background-color: #ff5733;'>T0044</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0045'><span class='test-square' style='background-color: #16a085;'>T0045</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0046'><span class='test-square' style='background-color: #ff9933;'>T0046</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0047'><span class='test-square' style='background-color: #ff99cc;'>T0047</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0048'><span class='test-square' style='background-color: #66ff33;'>T0048</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0049'><span class='test-square' style='background-color: #ff33cc;'>T0049</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0050'><span class='test-square' style='background-color: #66cc99;'>T0050</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0051'><span class='test-square' style='background-color: #66ffff;'>T0051</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0052'><span class='test-square' style='background-color: #00ff99;'>T0052</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0053'><span class='test-square' style='background-color: #ff9966;'>T0053</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0054'><span class='test-square' style='background-color: #ffcc00;'>T0054</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0055'><span class='test-square' style='background-color: #2ecc71;'>T0055</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0056'><span class='test-square' style='background-color: #ff6600;'>T0056</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0057'><span class='test-square' style='background-color: #cc6699;'>T0057</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0058'><span class='test-square' style='background-color: #33ccff;'>T0058</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0059'><span class='test-square' style='background-color: #ff6699;'>T0059</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0060'><span class='test-square' style='background-color: #ff3399;'>T0060</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0061'><span class='test-square' style='background-color: #9933ff;'>T0061</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0062'><span class='test-square' style='background-color: #cc6699;'>T0062</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0063'><span class='test-square' style='background-color: #99ccff;'>T0063</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0064'><span class='test-square' style='background-color: #2980b9;'>T0064</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0065'><span class='test-square' style='background-color: #6699ff;'>T0065</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0066'><span class='test-square' style='background-color: #00ff99;'>T0066</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0067'><span class='test-square' style='background-color: #33ff66;'>T0067</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0068'><span class='test-square' style='background-color: #ff3300;'>T0068</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0069'><span class='test-square' style='background-color: #33ff66;'>T0069</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0070'><span class='test-square' style='background-color: #27ae60;'>T0070</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0071'><span class='test-square' style='background-color: #ff0099;'>T0071</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0072'><span class='test-square' style='background-color: #2ecc71;'>T0072</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0073'><span class='test-square' style='background-color: #2980b9;'>T0073</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0074'><span class='test-square' style='background-color: #ff9933;'>T0074</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0075'><span class='test-square' style='background-color: #7f8c8d;'>T0075</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0076'><span class='test-square' style='background-color: #ff3300;'>T0076</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0077'><span class='test-square' style='background-color: #e67e22;'>T0077</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0078'><span class='test-square' style='background-color: #ff0066;'>T0078</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0079'><span class='test-square' style='background-color: #00ff66;'>T0079</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0080'><span class='test-square' style='background-color: #9933ff;'>T0080</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0081'><span class='test-square' style='background-color: #7f8c8d;'>T0081</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0082'><span class='test-square' style='background-color: #ff0099;'>T0082</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0083'><span class='test-square' style='background-color: #2980b9;'>T0083</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0084'><span class='test-square' style='background-color: #66cc99;'>T0084</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0085'><span class='test-square' style='background-color: #8e44ad;'>T0085</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0086'><span class='test-square' style='background-color: #66ff33;'>T0086</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0087'><span class='test-square' style='background-color: #ff5050;'>T0087</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0088'><span class='test-square' style='background-color: #cc33ff;'>T0088</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0089'><span class='test-square' style='background-color: #2c3e50;'>T0089</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0090'><span class='test-square' style='background-color: #ff6699;'>T0090</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0091'><span class='test-square' style='background-color: #e74c3c;'>T0091</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0092'><span class='test-square' style='background-color: #0099ff;'>T0092</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0093'><span class='test-square' style='background-color: #ff5733;'>T0093</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0094'><span class='test-square' style='background-color: #0099ff;'>T0094</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0095'><span class='test-square' style='background-color: #e74c3c;'>T0095</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0096'><span class='test-square' style='background-color: #cc6699;'>T0096</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0099;'>gemini-2.5-flash-preview-04-17</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0097'><span class='test-square' style='background-color: #ff3399;'>T0097</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #00ff99;'>gemini-2.5-pro-preview-05-06</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0098'><span class='test-square' style='background-color: #00ccff;'>T0098</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0099'><span class='test-square' style='background-color: #f1c40f;'>T0099</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0100'><span class='test-square' style='background-color: #ff9933;'>T0100</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0101'><span class='test-square' style='background-color: #ff6600;'>T0101</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0102'><span class='test-square' style='background-color: #ff3300;'>T0102</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0103'><span class='test-square' style='background-color: #ff3300;'>T0103</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0104'><span class='test-square' style='background-color: #3399ff;'>T0104</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0105'><span class='test-square' style='background-color: #00ccff;'>T0105</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0106'><span class='test-square' style='background-color: #ff6699;'>T0106</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0107'><span class='test-square' style='background-color: #c0392b;'>T0107</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0108'><span class='test-square' style='background-color: #c0392b;'>T0108</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0109'><span class='test-square' style='background-color: #ff5050;'>T0109</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0110'><span class='test-square' style='background-color: #6633ff;'>T0110</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0111'><span class='test-square' style='background-color: #99ff33;'>T0111</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0112'><span class='test-square' style='background-color: #3498db;'>T0112</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0113'><span class='test-square' style='background-color: #00ff99;'>T0113</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0114'><span class='test-square' style='background-color: #27ae60;'>T0114</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0115'><span class='test-square' style='background-color: #ccff00;'>T0115</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0116'><span class='test-square' style='background-color: #9966ff;'>T0116</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0117'><span class='test-square' style='background-color: #ff0099;'>T0117</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0118'><span class='test-square' style='background-color: #33ff66;'>T0118</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0119'><span class='test-square' style='background-color: #ff0066;'>T0119</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0120'><span class='test-square' style='background-color: #66ff33;'>T0120</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0121'><span class='test-square' style='background-color: #7f8c8d;'>T0121</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0122'><span class='test-square' style='background-color: #9b59b6;'>T0122</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0123'><span class='test-square' style='background-color: #ff6699;'>T0123</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0124'><span class='test-square' style='background-color: #ff6699;'>T0124</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0125'><span class='test-square' style='background-color: #cc6699;'>T0125</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0126'><span class='test-square' style='background-color: #99ccff;'>T0126</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0127'><span class='test-square' style='background-color: #2980b9;'>T0127</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0128'><span class='test-square' style='background-color: #f39c12;'>T0128</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0129'><span class='test-square' style='background-color: #c0392b;'>T0129</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0130'><span class='test-square' style='background-color: #99ff33;'>T0130</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0131'><span class='test-square' style='background-color: #2ecc71;'>T0131</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0132'><span class='test-square' style='background-color: #27ae60;'>T0132</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0133'><span class='test-square' style='background-color: #ff5050;'>T0133</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0134'><span class='test-square' style='background-color: #ffcc00;'>T0134</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0135'><span class='test-square' style='background-color: #cc6699;'>T0135</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0136'><span class='test-square' style='background-color: #99ff33;'>T0136</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0137'><span class='test-square' style='background-color: #6699ff;'>T0137</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0138'><span class='test-square' style='background-color: #ff0099;'>T0138</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0139'><span class='test-square' style='background-color: #9933ff;'>T0139</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0140'><span class='test-square' style='background-color: #3399ff;'>T0140</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0141'><span class='test-square' style='background-color: #ff5733;'>T0141</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0142'><span class='test-square' style='background-color: #66ff33;'>T0142</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0143'><span class='test-square' style='background-color: #66ffff;'>T0143</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0144'><span class='test-square' style='background-color: #ff5733;'>T0144</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0145'><span class='test-square' style='background-color: #00ccff;'>T0145</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0146'><span class='test-square' style='background-color: #6699ff;'>T0146</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0147'><span class='test-square' style='background-color: #c0392b;'>T0147</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0148'><span class='test-square' style='background-color: #3498db;'>T0148</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0149'><span class='test-square' style='background-color: #8e44ad;'>T0149</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0150'><span class='test-square' style='background-color: #ff33cc;'>T0150</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0151'><span class='test-square' style='background-color: #ffcc00;'>T0151</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0152'><span class='test-square' style='background-color: #0099ff;'>T0152</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0153'><span class='test-square' style='background-color: #ff6600;'>T0153</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0154'><span class='test-square' style='background-color: #ff3366;'>T0154</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0099;'>gemini-2.5-flash-preview-04-17</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0155'><span class='test-square' style='background-color: #ff5733;'>T0155</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0156'><span class='test-square' style='background-color: #00ff66;'>T0156</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0157'><span class='test-square' style='background-color: #cc33ff;'>T0157</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #00ff99;'>gemini-2.5-pro-preview-05-06</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0158'><span class='test-square' style='background-color: #ffcc00;'>T0158</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0159'><span class='test-square' style='background-color: #ff99cc;'>T0159</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0160'><span class='test-square' style='background-color: #2c3e50;'>T0160</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0161'><span class='test-square' style='background-color: #d35400;'>T0161</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0162'><span class='test-square' style='background-color: #66ff33;'>T0162</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0163'><span class='test-square' style='background-color: #34495e;'>T0163</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0164'><span class='test-square' style='background-color: #ff0066;'>T0164</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0165'><span class='test-square' style='background-color: #ccff00;'>T0165</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0166'><span class='test-square' style='background-color: #9966ff;'>T0166</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0167'><span class='test-square' style='background-color: #ff5733;'>T0167</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0168'><span class='test-square' style='background-color: #ff0066;'>T0168</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0169'><span class='test-square' style='background-color: #ff3300;'>T0169</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>mistral-medium-2508</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0170'><span class='test-square' style='background-color: #ffcc33;'>T0170</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #27ae60;'>mistral-medium-2505</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0171'><span class='test-square' style='background-color: #3498db;'>T0171</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>mistral-medium-2508</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0172'><span class='test-square' style='background-color: #ff0033;'>T0172</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #27ae60;'>mistral-medium-2505</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0173'><span class='test-square' style='background-color: #3399ff;'>T0173</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>mistral-medium-2508</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0174'><span class='test-square' style='background-color: #3399ff;'>T0174</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #27ae60;'>mistral-medium-2505</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0175'><span class='test-square' style='background-color: #ff6600;'>T0175</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>mistral-medium-2508</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0176'><span class='test-square' style='background-color: #1abc9c;'>T0176</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #27ae60;'>mistral-medium-2505</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0177'><span class='test-square' style='background-color: #ccff00;'>T0177</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>mistral-medium-2508</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0178'><span class='test-square' style='background-color: #ff0066;'>T0178</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #27ae60;'>mistral-medium-2505</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0179'><span class='test-square' style='background-color: #ff5733;'>T0179</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>mistral-medium-2508</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0180'><span class='test-square' style='background-color: #6699ff;'>T0180</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #27ae60;'>mistral-medium-2505</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0181'><span class='test-square' style='background-color: #ccff00;'>T0181</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #bdc3c7;'>pixtral-12b</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0182'><span class='test-square' style='background-color: #ff5733;'>T0182</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #bdc3c7;'>pixtral-12b</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0183'><span class='test-square' style='background-color: #cc33ff;'>T0183</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #bdc3c7;'>pixtral-12b</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0184'><span class='test-square' style='background-color: #6633ff;'>T0184</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #bdc3c7;'>pixtral-12b</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0185'><span class='test-square' style='background-color: #27ae60;'>T0185</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #bdc3c7;'>pixtral-12b</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0186'><span class='test-square' style='background-color: #0099ff;'>T0186</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #bdc3c7;'>pixtral-12b</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0187'><span class='test-square' style='background-color: #ff3399;'>T0187</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #d35400;'>mistral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0188'><span class='test-square' style='background-color: #f39c12;'>T0188</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #d35400;'>mistral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0189'><span class='test-square' style='background-color: #ff0099;'>T0189</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #d35400;'>mistral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0190'><span class='test-square' style='background-color: #ff9966;'>T0190</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #d35400;'>mistral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0191'><span class='test-square' style='background-color: #f1c40f;'>T0191</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #d35400;'>mistral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0192'><span class='test-square' style='background-color: #66ffff;'>T0192</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #d35400;'>mistral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0193'><span class='test-square' style='background-color: #0099ff;'>T0193</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0194'><span class='test-square' style='background-color: #ff0066;'>T0194</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0195'><span class='test-square' style='background-color: #9966ff;'>T0195</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0196'><span class='test-square' style='background-color: #ff6600;'>T0196</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0197'><span class='test-square' style='background-color: #ff6600;'>T0197</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0198'><span class='test-square' style='background-color: #ffcc33;'>T0198</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0199'><span class='test-square' style='background-color: #ff0099;'>T0199</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0200'><span class='test-square' style='background-color: #ff5050;'>T0200</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>gemini-2.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0201'><span class='test-square' style='background-color: #ff9933;'>T0201</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0202'><span class='test-square' style='background-color: #ff6600;'>T0202</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0203'><span class='test-square' style='background-color: #2ecc71;'>T0203</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0204'><span class='test-square' style='background-color: #ff6699;'>T0204</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0205'><span class='test-square' style='background-color: #3399ff;'>T0205</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0206'><span class='test-square' style='background-color: #ff6699;'>T0206</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0207'><span class='test-square' style='background-color: #ff3300;'>T0207</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0208'><span class='test-square' style='background-color: #ff0099;'>T0208</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>gemini-2.5-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0209'><span class='test-square' style='background-color: #ff99cc;'>T0209</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0210'><span class='test-square' style='background-color: #ff0099;'>T0210</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0211'><span class='test-square' style='background-color: #339933;'>T0211</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0212'><span class='test-square' style='background-color: #ff5050;'>T0212</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0213'><span class='test-square' style='background-color: #66ffff;'>T0213</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0214'><span class='test-square' style='background-color: #27ae60;'>T0214</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0215'><span class='test-square' style='background-color: #f39c12;'>T0215</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0216'><span class='test-square' style='background-color: #ff9966;'>T0216</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #6699ff;'>gemini-2.5-flash-lite-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0217'><span class='test-square' style='background-color: #339933;'>T0217</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0218'><span class='test-square' style='background-color: #ff0066;'>T0218</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0219'><span class='test-square' style='background-color: #00ccff;'>T0219</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0220'><span class='test-square' style='background-color: #ff3399;'>T0220</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0221'><span class='test-square' style='background-color: #9b59b6;'>T0221</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0222'><span class='test-square' style='background-color: #99ccff;'>T0222</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0223'><span class='test-square' style='background-color: #ff0033;'>T0223</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0224'><span class='test-square' style='background-color: #34495e;'>T0224</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0225'><span class='test-square' style='background-color: #bdc3c7;'>T0225</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>claude-sonnet-4-5-20250929</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0226'><span class='test-square' style='background-color: #cc33ff;'>T0226</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>claude-sonnet-4-5-20250929</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0227'><span class='test-square' style='background-color: #7f8c8d;'>T0227</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>claude-sonnet-4-5-20250929</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0228'><span class='test-square' style='background-color: #99ff33;'>T0228</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>claude-sonnet-4-5-20250929</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0229'><span class='test-square' style='background-color: #2ecc71;'>T0229</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>claude-sonnet-4-5-20250929</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0230'><span class='test-square' style='background-color: #e67e22;'>T0230</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>claude-sonnet-4-5-20250929</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0231'><span class='test-square' style='background-color: #ff3300;'>T0231</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/blacklist/">blacklist</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>Card</td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0232'><span class='test-square' style='background-color: #7f8c8d;'>T0232</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/blacklist/">blacklist</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Card</td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0233'><span class='test-square' style='background-color: #66ff33;'>T0233</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #33ff66;'>qwen/qwen3-vl-8b-thinking</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0234'><span class='test-square' style='background-color: #ff5733;'>T0234</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>meta-llama/llama-4-maverick</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0235'><span class='test-square' style='background-color: #27ae60;'>T0235</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/company_lists/">company_lists</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>ListPage</td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0236'><span class='test-square' style='background-color: #ff9933;'>T0236</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/company_lists/">company_lists</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gemini-2.5-flash-preview-09-2025</span></td>
    <td>ListPage</td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>prompt_min.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0237'><span class='test-square' style='background-color: #ff33cc;'>T0237</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>scicore</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>GLM-4.5V-FP8</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0238'><span class='test-square' style='background-color: #ff5050;'>T0238</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>scicore</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>GLM-4.5V-FP8</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0239'><span class='test-square' style='background-color: #ff3366;'>T0239</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>scicore</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>GLM-4.5V-FP8</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0240'><span class='test-square' style='background-color: #3399ff;'>T0240</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>scicore</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>GLM-4.5V-FP8</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0241'><span class='test-square' style='background-color: #ff6600;'>T0241</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>scicore</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>GLM-4.5V-FP8</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0242'><span class='test-square' style='background-color: #9b59b6;'>T0242</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>scicore</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>GLM-4.5V-FP8</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0243'><span class='test-square' style='background-color: #ff33cc;'>T0243</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #33ff66;'>qwen/qwen3-vl-8b-thinking</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0244'><span class='test-square' style='background-color: #ffcc33;'>T0244</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #33ff66;'>qwen/qwen3-vl-8b-thinking</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0245'><span class='test-square' style='background-color: #9b59b6;'>T0245</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #33ff66;'>qwen/qwen3-vl-8b-thinking</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0246'><span class='test-square' style='background-color: #ffcc00;'>T0246</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #33ff66;'>qwen/qwen3-vl-8b-thinking</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0247'><span class='test-square' style='background-color: #3498db;'>T0247</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #33ff66;'>qwen/qwen3-vl-8b-thinking</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0248'><span class='test-square' style='background-color: #6633ff;'>T0248</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>meta-llama/llama-4-maverick</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0249'><span class='test-square' style='background-color: #7f8c8d;'>T0249</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>meta-llama/llama-4-maverick</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0250'><span class='test-square' style='background-color: #99ccff;'>T0250</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>meta-llama/llama-4-maverick</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0251'><span class='test-square' style='background-color: #6699ff;'>T0251</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>meta-llama/llama-4-maverick</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='/humanities_data_benchmark/tests/T0252'><span class='test-square' style='background-color: #ff33cc;'>T0252</span></a></td>
    <td><a href="/humanities_data_benchmark/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>openrouter</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>meta-llama/llama-4-maverick</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>

  </tbody>
</table>

<script>
  $(document).ready(function() {
    $('#data-table').DataTable({
      "paging": true,
      "searching": true,
      "ordering": true,
      "info": true,
      "lengthMenu": [[10, 20, -1], [10, 20, "All"]],
    });
  });
</script>
