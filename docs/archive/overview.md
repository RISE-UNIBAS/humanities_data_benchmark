# Benchmark Overview

This page provides an overview of all benchmark tests.Click on the test name to see the detailed results.

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
</style>
<table id="data-table" class="display">
  <thead><tr>
    <th>Date</th>
    <th>bibliographic_data</th>
    <th>fraktur</th>
    <th>metadata_extraction</th>
    <th>test_benchmark</th>
    <th>test_benchmark2</th>

  </tr></thead>
  <tbody>
<tr>
    <td>2025-04-10</td>
    <td></td>
    <td></td>
    <td><a href='/archive/2025-04-10/T10'><span class='test-square' style='background-color: #ff6600;'>T10</span></a>&nbsp;<a href='/archive/2025-04-10/T11'><span class='test-square' style='background-color: #ff6600;'>T11</span></a>&nbsp;<a href='/archive/2025-04-10/T12'><span class='test-square' style='background-color: #6633ff;'>T12</span></a>&nbsp;<a href='/archive/2025-04-10/T13'><span class='test-square' style='background-color: #ff6600;'>T13</span></a>&nbsp;<a href='/archive/2025-04-10/T14'><span class='test-square' style='background-color: #34495e;'>T14</span></a>&nbsp;<a href='/archive/2025-04-10/T15'><span class='test-square' style='background-color: #ff0099;'>T15</span></a>&nbsp;<a href='/archive/2025-04-10/T16'><span class='test-square' style='background-color: #33ffcc;'>T16</span></a>&nbsp;<a href='/archive/2025-04-10/T17'><span class='test-square' style='background-color: #9b59b6;'>T17</span></a>&nbsp;<a href='/archive/2025-04-10/T18'><span class='test-square' style='background-color: #99ff33;'>T18</span></a>&nbsp;<a href='/archive/2025-04-10/T20'><span class='test-square' style='background-color: #ff5050;'>T20</span></a>&nbsp;<a href='/archive/2025-04-10/T23'><span class='test-square' style='background-color: #ff0066;'>T23</span></a>&nbsp;<a href='/archive/2025-04-10/T24'><span class='test-square' style='background-color: #e74c3c;'>T24</span></a>&nbsp;<a href='/archive/2025-04-10/T25'><span class='test-square' style='background-color: #ff6600;'>T25</span></a>&nbsp;<a href='/archive/2025-04-10/T36'><span class='test-square' style='background-color: #ff6699;'>T36</span></a>&nbsp;<a href='/archive/2025-04-10/T37'><span class='test-square' style='background-color: #ff9966;'>T37</span></a>&nbsp;<a href='/archive/2025-04-10/T38'><span class='test-square' style='background-color: #8e44ad;'>T38</span></a>&nbsp;<a href='/archive/2025-04-10/T39'><span class='test-square' style='background-color: #3498db;'>T39</span></a>&nbsp;<a href='/archive/2025-04-10/T40'><span class='test-square' style='background-color: #e67e22;'>T40</span></a>&nbsp;<a href='/archive/2025-04-10/T41'><span class='test-square' style='background-color: #ff0066;'>T41</span></a>&nbsp;<a href='/archive/2025-04-10/T42'><span class='test-square' style='background-color: #2980b9;'>T42</span></a>&nbsp;<a href='/archive/2025-04-10/T43'><span class='test-square' style='background-color: #ff0033;'>T43</span></a>&nbsp;<a href='/archive/2025-04-10/T44'><span class='test-square' style='background-color: #66ffff;'>T44</span></a>&nbsp;<a href='/archive/2025-04-10/T45'><span class='test-square' style='background-color: #2980b9;'>T45</span></a>&nbsp;<a href='/archive/2025-04-10/T48'><span class='test-square' style='background-color: #99ccff;'>T48</span></a>&nbsp;<a href='/archive/2025-04-10/T49'><span class='test-square' style='background-color: #ff6699;'>T49</span></a>&nbsp;<a href='/archive/2025-04-10/T52'><span class='test-square' style='background-color: #ff6600;'>T52</span></a>&nbsp;<a href='/archive/2025-04-10/T53'><span class='test-square' style='background-color: #ff9933;'>T53</span></a>&nbsp;<a href='/archive/2025-04-10/T56'><span class='test-square' style='background-color: #f39c12;'>T56</span></a>&nbsp;<a href='/archive/2025-04-10/T57'><span class='test-square' style='background-color: #99ff33;'>T57</span></a>&nbsp;<a href='/archive/2025-04-10/T60'><span class='test-square' style='background-color: #bdc3c7;'>T60</span></a>&nbsp;<a href='/archive/2025-04-10/T61'><span class='test-square' style='background-color: #2980b9;'>T61</span></a>&nbsp;<a href='/archive/2025-04-10/T62'><span class='test-square' style='background-color: #ff5733;'>T62</span></a>&nbsp;<a href='/archive/2025-04-10/T63'><span class='test-square' style='background-color: #6699ff;'>T63</span></a>&nbsp;<a href='/archive/2025-04-10/T64'><span class='test-square' style='background-color: #e67e22;'>T64</span></a>&nbsp;<a href='/archive/2025-04-10/T65'><span class='test-square' style='background-color: #9b59b6;'>T65</span></a>&nbsp;</td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-08</td>
    <td><a href='/archive/2025-04-08/T07'><span class='test-square' style='background-color: #ff99cc;'>T07</span></a>&nbsp;<a href='/archive/2025-04-08/T08'><span class='test-square' style='background-color: #ffcc33;'>T08</span></a>&nbsp;<a href='/archive/2025-04-08/T09'><span class='test-square' style='background-color: #ff0066;'>T09</span></a>&nbsp;<a href='/archive/2025-04-08/T26'><span class='test-square' style='background-color: #2ecc71;'>T26</span></a>&nbsp;<a href='/archive/2025-04-08/T27'><span class='test-square' style='background-color: #ff33cc;'>T27</span></a>&nbsp;<a href='/archive/2025-04-08/T29'><span class='test-square' style='background-color: #f39c12;'>T29</span></a>&nbsp;<a href='/archive/2025-04-08/T30'><span class='test-square' style='background-color: #1abc9c;'>T30</span></a>&nbsp;<a href='/archive/2025-04-08/T31'><span class='test-square' style='background-color: #9966ff;'>T31</span></a>&nbsp;<a href='/archive/2025-04-08/T33'><span class='test-square' style='background-color: #9b59b6;'>T33</span></a>&nbsp;<a href='/archive/2025-04-08/T35'><span class='test-square' style='background-color: #2c3e50;'>T35</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-07</td>
    <td></td>
    <td></td>
    <td><a href='/archive/2025-04-07/T17'><span class='test-square' style='background-color: #9b59b6;'>T17</span></a>&nbsp;<a href='/archive/2025-04-07/T24'><span class='test-square' style='background-color: #e74c3c;'>T24</span></a>&nbsp;<a href='/archive/2025-04-07/T25'><span class='test-square' style='background-color: #ff6600;'>T25</span></a>&nbsp;</td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-02</td>
    <td></td>
    <td><a href='/archive/2025-04-02/T22'><span class='test-square' style='background-color: #2980b9;'>T22</span></a>&nbsp;</td>
    <td><a href='/archive/2025-04-02/T23'><span class='test-square' style='background-color: #ff0066;'>T23</span></a>&nbsp;</td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-01</td>
    <td><a href='/archive/2025-04-01/T07'><span class='test-square' style='background-color: #ff99cc;'>T07</span></a>&nbsp;<a href='/archive/2025-04-01/T08'><span class='test-square' style='background-color: #ffcc33;'>T08</span></a>&nbsp;<a href='/archive/2025-04-01/T09'><span class='test-square' style='background-color: #ff0066;'>T09</span></a>&nbsp;</td>
    <td></td>
    <td><a href='/archive/2025-04-01/T10'><span class='test-square' style='background-color: #ff6600;'>T10</span></a>&nbsp;<a href='/archive/2025-04-01/T11'><span class='test-square' style='background-color: #ff6600;'>T11</span></a>&nbsp;<a href='/archive/2025-04-01/T12'><span class='test-square' style='background-color: #6633ff;'>T12</span></a>&nbsp;<a href='/archive/2025-04-01/T13'><span class='test-square' style='background-color: #ff6600;'>T13</span></a>&nbsp;<a href='/archive/2025-04-01/T14'><span class='test-square' style='background-color: #34495e;'>T14</span></a>&nbsp;<a href='/archive/2025-04-01/T15'><span class='test-square' style='background-color: #ff0099;'>T15</span></a>&nbsp;<a href='/archive/2025-04-01/T16'><span class='test-square' style='background-color: #33ffcc;'>T16</span></a>&nbsp;<a href='/archive/2025-04-01/T17'><span class='test-square' style='background-color: #9b59b6;'>T17</span></a>&nbsp;<a href='/archive/2025-04-01/T18'><span class='test-square' style='background-color: #99ff33;'>T18</span></a>&nbsp;<a href='/archive/2025-04-01/T19'><span class='test-square' style='background-color: #0099ff;'>T19</span></a>&nbsp;<a href='/archive/2025-04-01/T20'><span class='test-square' style='background-color: #ff5050;'>T20</span></a>&nbsp;<a href='/archive/2025-04-01/T21'><span class='test-square' style='background-color: #9933ff;'>T21</span></a>&nbsp;</td>
    <td><a href='/archive/2025-04-01/T01'><span class='test-square' style='background-color: #99ccff;'>T01</span></a>&nbsp;<a href='/archive/2025-04-01/T02'><span class='test-square' style='background-color: #0099ff;'>T02</span></a>&nbsp;<a href='/archive/2025-04-01/T03'><span class='test-square' style='background-color: #33ccff;'>T03</span></a>&nbsp;</td>
    <td><a href='/archive/2025-04-01/T04'><span class='test-square' style='background-color: #ff3300;'>T04</span></a>&nbsp;<a href='/archive/2025-04-01/T05'><span class='test-square' style='background-color: #2c3e50;'>T05</span></a>&nbsp;<a href='/archive/2025-04-01/T06'><span class='test-square' style='background-color: #33ccff;'>T06</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-03-05</td>
    <td><a href='/archive/2025-03-05/T07'><span class='test-square' style='background-color: #ff99cc;'>T07</span></a>&nbsp;<a href='/archive/2025-03-05/T08'><span class='test-square' style='background-color: #ffcc33;'>T08</span></a>&nbsp;<a href='/archive/2025-03-05/T09'><span class='test-square' style='background-color: #ff0066;'>T09</span></a>&nbsp;</td>
    <td></td>
    <td><a href='/archive/2025-03-05/T10'><span class='test-square' style='background-color: #ff6600;'>T10</span></a>&nbsp;<a href='/archive/2025-03-05/T11'><span class='test-square' style='background-color: #ff6600;'>T11</span></a>&nbsp;<a href='/archive/2025-03-05/T12'><span class='test-square' style='background-color: #6633ff;'>T12</span></a>&nbsp;<a href='/archive/2025-03-05/T13'><span class='test-square' style='background-color: #ff6600;'>T13</span></a>&nbsp;<a href='/archive/2025-03-05/T14'><span class='test-square' style='background-color: #34495e;'>T14</span></a>&nbsp;<a href='/archive/2025-03-05/T15'><span class='test-square' style='background-color: #ff0099;'>T15</span></a>&nbsp;<a href='/archive/2025-03-05/T16'><span class='test-square' style='background-color: #33ffcc;'>T16</span></a>&nbsp;<a href='/archive/2025-03-05/T17'><span class='test-square' style='background-color: #9b59b6;'>T17</span></a>&nbsp;<a href='/archive/2025-03-05/T18'><span class='test-square' style='background-color: #99ff33;'>T18</span></a>&nbsp;</td>
    <td><a href='/archive/2025-03-05/T01'><span class='test-square' style='background-color: #99ccff;'>T01</span></a>&nbsp;<a href='/archive/2025-03-05/T02'><span class='test-square' style='background-color: #0099ff;'>T02</span></a>&nbsp;<a href='/archive/2025-03-05/T03'><span class='test-square' style='background-color: #33ccff;'>T03</span></a>&nbsp;</td>
    <td><a href='/archive/2025-03-05/T04'><span class='test-square' style='background-color: #ff3300;'>T04</span></a>&nbsp;<a href='/archive/2025-03-05/T05'><span class='test-square' style='background-color: #2c3e50;'>T05</span></a>&nbsp;<a href='/archive/2025-03-05/T06'><span class='test-square' style='background-color: #33ccff;'>T06</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-03-04</td>
    <td><a href='/archive/2025-03-04/T07'><span class='test-square' style='background-color: #ff99cc;'>T07</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/archive/2025-03-04/T01'><span class='test-square' style='background-color: #99ccff;'>T01</span></a>&nbsp;</td>
    <td></td>
</tr>
<tr>
    <td>2025-03-02</td>
    <td><a href='/archive/2025-03-02/T07'><span class='test-square' style='background-color: #ff99cc;'>T07</span></a>&nbsp;<a href='/archive/2025-03-02/T08'><span class='test-square' style='background-color: #ffcc33;'>T08</span></a>&nbsp;<a href='/archive/2025-03-02/T09'><span class='test-square' style='background-color: #ff0066;'>T09</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/archive/2025-03-02/T06'><span class='test-square' style='background-color: #33ccff;'>T06</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-03-01</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/archive/2025-03-01/T01'><span class='test-square' style='background-color: #99ccff;'>T01</span></a>&nbsp;<a href='/archive/2025-03-01/T02'><span class='test-square' style='background-color: #0099ff;'>T02</span></a>&nbsp;<a href='/archive/2025-03-01/T03'><span class='test-square' style='background-color: #33ccff;'>T03</span></a>&nbsp;</td>
    <td><a href='/archive/2025-03-01/T04'><span class='test-square' style='background-color: #ff3300;'>T04</span></a>&nbsp;<a href='/archive/2025-03-01/T05'><span class='test-square' style='background-color: #2c3e50;'>T05</span></a>&nbsp;</td>
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
