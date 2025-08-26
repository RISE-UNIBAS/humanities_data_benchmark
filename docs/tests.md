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
    .inner-table td:nth-child(5) {
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
    <td><a href='tests/T01'><span class='test-square' style='background-color: #99ccff;'>T01</span></a></td>
    <td><a href="/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T02'><span class='test-square' style='background-color: #0099ff;'>T02</span></a></td>
    <td><a href="/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T03'><span class='test-square' style='background-color: #33ccff;'>T03</span></a></td>
    <td><a href="/benchmarks/test_benchmark/">test_benchmark</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T04'><span class='test-square' style='background-color: #ff3300;'>T04</span></a></td>
    <td><a href="/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T05'><span class='test-square' style='background-color: #2c3e50;'>T05</span></a></td>
    <td><a href="/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T06'><span class='test-square' style='background-color: #33ccff;'>T06</span></a></td>
    <td><a href="/benchmarks/test_benchmark2/">test_benchmark2</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td></td>
    <td>0.5</td>
    <td>You are a Historian</td>
    <td>a_prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T07'><span class='test-square' style='background-color: #ff99cc;'>T07</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T08'><span class='test-square' style='background-color: #ffcc33;'>T08</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T09'><span class='test-square' style='background-color: #ff0066;'>T09</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T10'><span class='test-square' style='background-color: #ff6600;'>T10</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T11'><span class='test-square' style='background-color: #ff6600;'>T11</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T12'><span class='test-square' style='background-color: #6633ff;'>T12</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T13'><span class='test-square' style='background-color: #ff6600;'>T13</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T14'><span class='test-square' style='background-color: #34495e;'>T14</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T15'><span class='test-square' style='background-color: #ff0099;'>T15</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T16'><span class='test-square' style='background-color: #33ffcc;'>T16</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T17'><span class='test-square' style='background-color: #9b59b6;'>T17</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T18'><span class='test-square' style='background-color: #99ff33;'>T18</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T19'><span class='test-square' style='background-color: #0099ff;'>T19</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T20'><span class='test-square' style='background-color: #ff5050;'>T20</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T21'><span class='test-square' style='background-color: #9933ff;'>T21</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T22'><span class='test-square' style='background-color: #2980b9;'>T22</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T23'><span class='test-square' style='background-color: #ff0066;'>T23</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T24'><span class='test-square' style='background-color: #e74c3c;'>T24</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T25'><span class='test-square' style='background-color: #ff6600;'>T25</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T26'><span class='test-square' style='background-color: #2ecc71;'>T26</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T27'><span class='test-square' style='background-color: #ff33cc;'>T27</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T28'><span class='test-square' style='background-color: #cc33ff;'>T28</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T29'><span class='test-square' style='background-color: #f39c12;'>T29</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T30'><span class='test-square' style='background-color: #1abc9c;'>T30</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T31'><span class='test-square' style='background-color: #9966ff;'>T31</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T32'><span class='test-square' style='background-color: #1abc9c;'>T32</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T33'><span class='test-square' style='background-color: #9b59b6;'>T33</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T34'><span class='test-square' style='background-color: #33ffcc;'>T34</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T35'><span class='test-square' style='background-color: #2c3e50;'>T35</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T36'><span class='test-square' style='background-color: #ff6699;'>T36</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T37'><span class='test-square' style='background-color: #ff9966;'>T37</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T38'><span class='test-square' style='background-color: #8e44ad;'>T38</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T39'><span class='test-square' style='background-color: #3498db;'>T39</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T40'><span class='test-square' style='background-color: #e67e22;'>T40</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T41'><span class='test-square' style='background-color: #ff0066;'>T41</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T42'><span class='test-square' style='background-color: #2980b9;'>T42</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T43'><span class='test-square' style='background-color: #ff0033;'>T43</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T44'><span class='test-square' style='background-color: #66ffff;'>T44</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T45'><span class='test-square' style='background-color: #2980b9;'>T45</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T46'><span class='test-square' style='background-color: #9933ff;'>T46</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T47'><span class='test-square' style='background-color: #e67e22;'>T47</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T48'><span class='test-square' style='background-color: #99ccff;'>T48</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T49'><span class='test-square' style='background-color: #ff6699;'>T49</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T50'><span class='test-square' style='background-color: #ff3399;'>T50</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T51'><span class='test-square' style='background-color: #ccff00;'>T51</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T52'><span class='test-square' style='background-color: #ff6600;'>T52</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T53'><span class='test-square' style='background-color: #ff9933;'>T53</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T54'><span class='test-square' style='background-color: #3399ff;'>T54</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T55'><span class='test-square' style='background-color: #99ccff;'>T55</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T56'><span class='test-square' style='background-color: #f39c12;'>T56</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T57'><span class='test-square' style='background-color: #99ff33;'>T57</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T58'><span class='test-square' style='background-color: #16a085;'>T58</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T59'><span class='test-square' style='background-color: #33ccff;'>T59</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T60'><span class='test-square' style='background-color: #bdc3c7;'>T60</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T61'><span class='test-square' style='background-color: #2980b9;'>T61</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history. You only return valid JSON an no other text.</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T62'><span class='test-square' style='background-color: #ff5733;'>T62</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T63'><span class='test-square' style='background-color: #6699ff;'>T63</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T64'><span class='test-square' style='background-color: #e67e22;'>T64</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T65'><span class='test-square' style='background-color: #9b59b6;'>T65</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-3-5-haiku-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T66'><span class='test-square' style='background-color: #7f8c8d;'>T66</span></a></td>
    <td><a href="/benchmarks/zettelkatalog/">zettelkatalog</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T67'><span class='test-square' style='background-color: #c0392b;'>T67</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T68'><span class='test-square' style='background-color: #f39c12;'>T68</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T69'><span class='test-square' style='background-color: #00ccff;'>T69</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T70'><span class='test-square' style='background-color: #27ae60;'>T70</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T71'><span class='test-square' style='background-color: #ff6600;'>T71</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T72'><span class='test-square' style='background-color: #3498db;'>T72</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T73'><span class='test-square' style='background-color: #8e44ad;'>T73</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T74'><span class='test-square' style='background-color: #00ff99;'>T74</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T75'><span class='test-square' style='background-color: #34495e;'>T75</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T76'><span class='test-square' style='background-color: #2ecc71;'>T76</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T77'><span class='test-square' style='background-color: #0099ff;'>T77</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T78'><span class='test-square' style='background-color: #0099ff;'>T78</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T79'><span class='test-square' style='background-color: #3399ff;'>T79</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #33ccff;'>gpt-4o</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T80'><span class='test-square' style='background-color: #ff0066;'>T80</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e74c3c;'>gemini-2.5-pro-exp-03-25</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T81'><span class='test-square' style='background-color: #ffcc33;'>T81</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.5-preview</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T82'><span class='test-square' style='background-color: #00ff99;'>T82</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>gpt-4o-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T83'><span class='test-square' style='background-color: #16a085;'>T83</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>gpt-4.1</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T84'><span class='test-square' style='background-color: #ff99cc;'>T84</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gpt-4.1-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T85'><span class='test-square' style='background-color: #ffcc00;'>T85</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>gpt-4.1-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T86'><span class='test-square' style='background-color: #d35400;'>T86</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #f39c12;'>gemini-2.0-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T87'><span class='test-square' style='background-color: #ff9966;'>T87</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #9b59b6;'>gemini-exp-1206</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T88'><span class='test-square' style='background-color: #f39c12;'>T88</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #2ecc71;'>gemini-1.5-flash</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T89'><span class='test-square' style='background-color: #33ffcc;'>T89</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #3399ff;'>gemini-1.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T90'><span class='test-square' style='background-color: #6699ff;'>T90</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0033;'>gemini-2.0-flash-lite</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T91'><span class='test-square' style='background-color: #ff6600;'>T91</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #7f8c8d;'>gemini-2.0-pro-exp-02-05</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T92'><span class='test-square' style='background-color: #9b59b6;'>T92</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-3-7-sonnet-20250219</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T93'><span class='test-square' style='background-color: #6699ff;'>T93</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #cc6699;'>claude-3-5-sonnet-20241022</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T94'><span class='test-square' style='background-color: #ff9966;'>T94</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #99ff33;'>claude-3-opus-20240229</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T95'><span class='test-square' style='background-color: #2980b9;'>T95</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>mistral</span></td>
    <td><span class='test-rectangle' style='background-color: #34495e;'>pixtral-large-latest</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T96'><span class='test-square' style='background-color: #9b59b6;'>T96</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff0099;'>gemini-2.5-flash-preview-04-17</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T97'><span class='test-square' style='background-color: #ff6699;'>T97</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #00ff99;'>gemini-2.5-pro-preview-05-06</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>true</td>
</tr>
<tr>
    <td><a href='tests/T98'><span class='test-square' style='background-color: #66ff33;'>T98</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T99'><span class='test-square' style='background-color: #2980b9;'>T99</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T100'><span class='test-square' style='background-color: #34495e;'>T100</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T101'><span class='test-square' style='background-color: #33ffcc;'>T101</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T102'><span class='test-square' style='background-color: #ff99cc;'>T102</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T103'><span class='test-square' style='background-color: #3399ff;'>T103</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T104'><span class='test-square' style='background-color: #3399ff;'>T104</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T105'><span class='test-square' style='background-color: #ffcc33;'>T105</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T106'><span class='test-square' style='background-color: #ff6600;'>T106</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #ff6600;'>claude-opus-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T107'><span class='test-square' style='background-color: #27ae60;'>T107</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #f1c40f;'>claude-sonnet-4-20250514</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T108'><span class='test-square' style='background-color: #cc6699;'>T108</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T109'><span class='test-square' style='background-color: #ccff00;'>T109</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T110'><span class='test-square' style='background-color: #ff9933;'>T110</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T111'><span class='test-square' style='background-color: #2980b9;'>T111</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T112'><span class='test-square' style='background-color: #34495e;'>T112</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T113'><span class='test-square' style='background-color: #33ccff;'>T113</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T114'><span class='test-square' style='background-color: #bdc3c7;'>T114</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T115'><span class='test-square' style='background-color: #ccff00;'>T115</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T116'><span class='test-square' style='background-color: #cc6699;'>T116</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T117'><span class='test-square' style='background-color: #ffcc33;'>T117</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T118'><span class='test-square' style='background-color: #33cccc;'>T118</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T119'><span class='test-square' style='background-color: #33ff66;'>T119</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T120'><span class='test-square' style='background-color: #6633ff;'>T120</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T121'><span class='test-square' style='background-color: #9b59b6;'>T121</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T122'><span class='test-square' style='background-color: #f39c12;'>T122</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T123'><span class='test-square' style='background-color: #ffcc33;'>T123</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T124'><span class='test-square' style='background-color: #ff3366;'>T124</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T125'><span class='test-square' style='background-color: #3498db;'>T125</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T126'><span class='test-square' style='background-color: #66ff33;'>T126</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T127'><span class='test-square' style='background-color: #0099ff;'>T127</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff5050;'>anthropic</span></td>
    <td><span class='test-rectangle' style='background-color: #0099ff;'>claude-opus-4-1-20250805</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T128'><span class='test-square' style='background-color: #8e44ad;'>T128</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T129'><span class='test-square' style='background-color: #bdc3c7;'>T129</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff9933;'>gpt-5</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T130'><span class='test-square' style='background-color: #ff0099;'>T130</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #8e44ad;'>gpt-5-mini</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T131'><span class='test-square' style='background-color: #c0392b;'>T131</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #ff33cc;'>gpt-5-nano</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T132'><span class='test-square' style='background-color: #00ff66;'>T132</span></a></td>
    <td><a href="/benchmarks/fraktur/">fraktur</a></td>
    <td><span class='test-rectangle' style='background-color: #ffcc33;'>genai</span></td>
    <td><span class='test-rectangle' style='background-color: #e67e22;'>gemini-2.5-pro</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge</td>
    <td>prompt_optimized.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T133'><span class='test-square' style='background-color: #d35400;'>T133</span></a></td>
    <td><a href="/benchmarks/bibliographic_data/">bibliographic_data</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a Historian</td>
    <td></td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T134'><span class='test-square' style='background-color: #6699ff;'>T134</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T135'><span class='test-square' style='background-color: #9b59b6;'>T135</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
    <td>prompt.txt</td>
    <td>false</td>
</tr>
<tr>
    <td><a href='tests/T136'><span class='test-square' style='background-color: #ff5733;'>T136</span></a></td>
    <td><a href="/benchmarks/metadata_extraction/">metadata_extraction</a></td>
    <td><span class='test-rectangle' style='background-color: #ff0066;'>openai</span></td>
    <td><span class='test-rectangle' style='background-color: #2980b9;'>o3</span></td>
    <td>Document</td>
    <td>0.0</td>
    <td>You are a historian with keyword knowledge and an expert in the field of 20th century Swiss history</td>
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
