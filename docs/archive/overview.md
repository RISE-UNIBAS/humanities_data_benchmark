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
    <th>Date</th>
    <th>bibliographic_data</th>
    <th>blacklist</th>
    <th>company_lists</th>
    <th>fraktur</th>
    <th>metadata_extraction</th>
    <th>test_benchmark</th>
    <th>test_benchmark2</th>
    <th>zettelkatalog</th>

  </tr></thead>
  <tbody>
<tr>
    <td>2025-10-20</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-20/T0253'><span class='test-square' style='background-color: #33ff66;'>T0253</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0259'><span class='test-square' style='background-color: #6699ff;'>T0259</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0265'><span class='test-square' style='background-color: #ff6600;'>T0265</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-20/T0257'><span class='test-square' style='background-color: #ff3366;'>T0257</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0263'><span class='test-square' style='background-color: #9966ff;'>T0263</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0269'><span class='test-square' style='background-color: #bdc3c7;'>T0269</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-20/T0254'><span class='test-square' style='background-color: #ccff00;'>T0254</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0255'><span class='test-square' style='background-color: #e67e22;'>T0255</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0256'><span class='test-square' style='background-color: #6699ff;'>T0256</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0260'><span class='test-square' style='background-color: #339933;'>T0260</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0261'><span class='test-square' style='background-color: #33ccff;'>T0261</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0262'><span class='test-square' style='background-color: #34495e;'>T0262</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0266'><span class='test-square' style='background-color: #f1c40f;'>T0266</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0267'><span class='test-square' style='background-color: #ff9966;'>T0267</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0268'><span class='test-square' style='background-color: #00ff66;'>T0268</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-20/T0258'><span class='test-square' style='background-color: #ff99cc;'>T0258</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0264'><span class='test-square' style='background-color: #2ecc71;'>T0264</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-20/T0270'><span class='test-square' style='background-color: #ff9933;'>T0270</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-10-17</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-17/T0233'><span class='test-square' style='background-color: #66ff33;'>T0233</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0234'><span class='test-square' style='background-color: #ff5733;'>T0234</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0237'><span class='test-square' style='background-color: #ff33cc;'>T0237</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-17/T0241'><span class='test-square' style='background-color: #ff6600;'>T0241</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0246'><span class='test-square' style='background-color: #ffcc00;'>T0246</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0251'><span class='test-square' style='background-color: #6699ff;'>T0251</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-17/T0238'><span class='test-square' style='background-color: #ff5050;'>T0238</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0239'><span class='test-square' style='background-color: #ff3366;'>T0239</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0240'><span class='test-square' style='background-color: #3399ff;'>T0240</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0243'><span class='test-square' style='background-color: #ff33cc;'>T0243</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0244'><span class='test-square' style='background-color: #ffcc33;'>T0244</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0245'><span class='test-square' style='background-color: #9b59b6;'>T0245</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0248'><span class='test-square' style='background-color: #6633ff;'>T0248</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0249'><span class='test-square' style='background-color: #7f8c8d;'>T0249</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0250'><span class='test-square' style='background-color: #99ccff;'>T0250</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-17/T0242'><span class='test-square' style='background-color: #9b59b6;'>T0242</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0247'><span class='test-square' style='background-color: #3498db;'>T0247</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-17/T0252'><span class='test-square' style='background-color: #ff33cc;'>T0252</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-10-03</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-03/T0164'><span class='test-square' style='background-color: #ff0066;'>T0164</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-10-02</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-02/T0161'><span class='test-square' style='background-color: #d35400;'>T0161</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-02/T0162'><span class='test-square' style='background-color: #66ff33;'>T0162</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-10-01</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-01/T0129'><span class='test-square' style='background-color: #c0392b;'>T0129</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0130'><span class='test-square' style='background-color: #99ff33;'>T0130</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0131'><span class='test-square' style='background-color: #2ecc71;'>T0131</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0133'><span class='test-square' style='background-color: #ff5050;'>T0133</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0138'><span class='test-square' style='background-color: #ff0099;'>T0138</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0139'><span class='test-square' style='background-color: #9933ff;'>T0139</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0140'><span class='test-square' style='background-color: #3399ff;'>T0140</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0141'><span class='test-square' style='background-color: #ff5733;'>T0141</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0169'><span class='test-square' style='background-color: #ff3300;'>T0169</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0170'><span class='test-square' style='background-color: #ffcc33;'>T0170</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0181'><span class='test-square' style='background-color: #ccff00;'>T0181</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0187'><span class='test-square' style='background-color: #ff3399;'>T0187</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0203'><span class='test-square' style='background-color: #2ecc71;'>T0203</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0211'><span class='test-square' style='background-color: #339933;'>T0211</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0219'><span class='test-square' style='background-color: #00ccff;'>T0219</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0225'><span class='test-square' style='background-color: #bdc3c7;'>T0225</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-01/T0132'><span class='test-square' style='background-color: #27ae60;'>T0132</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0137'><span class='test-square' style='background-color: #6699ff;'>T0137</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0177'><span class='test-square' style='background-color: #ccff00;'>T0177</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0178'><span class='test-square' style='background-color: #ff0066;'>T0178</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0185'><span class='test-square' style='background-color: #27ae60;'>T0185</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0191'><span class='test-square' style='background-color: #f1c40f;'>T0191</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0207'><span class='test-square' style='background-color: #ff3300;'>T0207</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0215'><span class='test-square' style='background-color: #f39c12;'>T0215</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0223'><span class='test-square' style='background-color: #ff0033;'>T0223</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0229'><span class='test-square' style='background-color: #2ecc71;'>T0229</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-01/T0134'><span class='test-square' style='background-color: #ffcc00;'>T0134</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0135'><span class='test-square' style='background-color: #cc6699;'>T0135</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0136'><span class='test-square' style='background-color: #99ff33;'>T0136</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0171'><span class='test-square' style='background-color: #3498db;'>T0171</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0172'><span class='test-square' style='background-color: #ff0033;'>T0172</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0173'><span class='test-square' style='background-color: #3399ff;'>T0173</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0174'><span class='test-square' style='background-color: #3399ff;'>T0174</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0175'><span class='test-square' style='background-color: #ff6600;'>T0175</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0176'><span class='test-square' style='background-color: #1abc9c;'>T0176</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0182'><span class='test-square' style='background-color: #ff5733;'>T0182</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0183'><span class='test-square' style='background-color: #cc33ff;'>T0183</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0184'><span class='test-square' style='background-color: #6633ff;'>T0184</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0188'><span class='test-square' style='background-color: #f39c12;'>T0188</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0189'><span class='test-square' style='background-color: #ff0099;'>T0189</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0190'><span class='test-square' style='background-color: #ff9966;'>T0190</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0204'><span class='test-square' style='background-color: #ff6699;'>T0204</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0205'><span class='test-square' style='background-color: #3399ff;'>T0205</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0206'><span class='test-square' style='background-color: #ff6699;'>T0206</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0212'><span class='test-square' style='background-color: #ff5050;'>T0212</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0213'><span class='test-square' style='background-color: #66ffff;'>T0213</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0214'><span class='test-square' style='background-color: #27ae60;'>T0214</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0220'><span class='test-square' style='background-color: #ff3399;'>T0220</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0221'><span class='test-square' style='background-color: #9b59b6;'>T0221</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0222'><span class='test-square' style='background-color: #99ccff;'>T0222</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0226'><span class='test-square' style='background-color: #cc33ff;'>T0226</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0227'><span class='test-square' style='background-color: #7f8c8d;'>T0227</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0228'><span class='test-square' style='background-color: #99ff33;'>T0228</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-01/T0201'><span class='test-square' style='background-color: #ff9933;'>T0201</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0209'><span class='test-square' style='background-color: #ff99cc;'>T0209</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0217'><span class='test-square' style='background-color: #339933;'>T0217</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-01/T0202'><span class='test-square' style='background-color: #ff6600;'>T0202</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0210'><span class='test-square' style='background-color: #ff0099;'>T0210</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0218'><span class='test-square' style='background-color: #ff0066;'>T0218</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-10-01/T0143'><span class='test-square' style='background-color: #66ffff;'>T0143</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0144'><span class='test-square' style='background-color: #ff5733;'>T0144</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0145'><span class='test-square' style='background-color: #00ccff;'>T0145</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0146'><span class='test-square' style='background-color: #6699ff;'>T0146</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0147'><span class='test-square' style='background-color: #c0392b;'>T0147</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0148'><span class='test-square' style='background-color: #3498db;'>T0148</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0151'><span class='test-square' style='background-color: #ffcc00;'>T0151</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0152'><span class='test-square' style='background-color: #0099ff;'>T0152</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0155'><span class='test-square' style='background-color: #ff5733;'>T0155</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0159'><span class='test-square' style='background-color: #ff99cc;'>T0159</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0160'><span class='test-square' style='background-color: #2c3e50;'>T0160</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0165'><span class='test-square' style='background-color: #ccff00;'>T0165</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0166'><span class='test-square' style='background-color: #9966ff;'>T0166</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0167'><span class='test-square' style='background-color: #ff5733;'>T0167</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0168'><span class='test-square' style='background-color: #ff0066;'>T0168</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0179'><span class='test-square' style='background-color: #ff5733;'>T0179</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0180'><span class='test-square' style='background-color: #6699ff;'>T0180</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0186'><span class='test-square' style='background-color: #0099ff;'>T0186</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0192'><span class='test-square' style='background-color: #66ffff;'>T0192</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0208'><span class='test-square' style='background-color: #ff0099;'>T0208</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0216'><span class='test-square' style='background-color: #ff9966;'>T0216</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-10-01/T0224'><span class='test-square' style='background-color: #34495e;'>T0224</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-09-30</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-30/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0008'><span class='test-square' style='background-color: #ffcc00;'>T0008</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0009'><span class='test-square' style='background-color: #f39c12;'>T0009</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0027'><span class='test-square' style='background-color: #ff9966;'>T0027</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0031'><span class='test-square' style='background-color: #ff0099;'>T0031</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0033'><span class='test-square' style='background-color: #f39c12;'>T0033</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0035'><span class='test-square' style='background-color: #6699ff;'>T0035</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0106'><span class='test-square' style='background-color: #ff6699;'>T0106</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0107'><span class='test-square' style='background-color: #c0392b;'>T0107</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0127'><span class='test-square' style='background-color: #2980b9;'>T0127</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0128'><span class='test-square' style='background-color: #f39c12;'>T0128</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0129'><span class='test-square' style='background-color: #c0392b;'>T0129</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0130'><span class='test-square' style='background-color: #99ff33;'>T0130</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0131'><span class='test-square' style='background-color: #2ecc71;'>T0131</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0133'><span class='test-square' style='background-color: #ff5050;'>T0133</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0195'><span class='test-square' style='background-color: #9966ff;'>T0195</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-30/T0079'><span class='test-square' style='background-color: #00ff66;'>T0079</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0082'><span class='test-square' style='background-color: #ff0099;'>T0082</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0083'><span class='test-square' style='background-color: #2980b9;'>T0083</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0084'><span class='test-square' style='background-color: #66cc99;'>T0084</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0085'><span class='test-square' style='background-color: #8e44ad;'>T0085</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0086'><span class='test-square' style='background-color: #66ff33;'>T0086</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0090'><span class='test-square' style='background-color: #ff6699;'>T0090</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0092'><span class='test-square' style='background-color: #0099ff;'>T0092</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0093'><span class='test-square' style='background-color: #ff5733;'>T0093</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0094'><span class='test-square' style='background-color: #0099ff;'>T0094</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0095'><span class='test-square' style='background-color: #e74c3c;'>T0095</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0098'><span class='test-square' style='background-color: #00ccff;'>T0098</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0099'><span class='test-square' style='background-color: #f1c40f;'>T0099</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0120'><span class='test-square' style='background-color: #66ff33;'>T0120</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0121'><span class='test-square' style='background-color: #7f8c8d;'>T0121</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0122'><span class='test-square' style='background-color: #9b59b6;'>T0122</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0123'><span class='test-square' style='background-color: #ff6699;'>T0123</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0132'><span class='test-square' style='background-color: #27ae60;'>T0132</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0199'><span class='test-square' style='background-color: #ff0099;'>T0199</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-30/T0010'><span class='test-square' style='background-color: #99ff33;'>T0010</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0012'><span class='test-square' style='background-color: #ff6600;'>T0012</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0013'><span class='test-square' style='background-color: #0099ff;'>T0013</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0017'><span class='test-square' style='background-color: #ff6600;'>T0017</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0018'><span class='test-square' style='background-color: #ff9966;'>T0018</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0020'><span class='test-square' style='background-color: #16a085;'>T0020</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0023'><span class='test-square' style='background-color: #33ffcc;'>T0023</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0024'><span class='test-square' style='background-color: #ff33cc;'>T0024</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0025'><span class='test-square' style='background-color: #33ff66;'>T0025</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0036'><span class='test-square' style='background-color: #ff6600;'>T0036</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0038'><span class='test-square' style='background-color: #ff9966;'>T0038</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0039'><span class='test-square' style='background-color: #66cc99;'>T0039</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0042'><span class='test-square' style='background-color: #c0392b;'>T0042</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0043'><span class='test-square' style='background-color: #00ffcc;'>T0043</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0044'><span class='test-square' style='background-color: #ff5733;'>T0044</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0045'><span class='test-square' style='background-color: #16a085;'>T0045</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0052'><span class='test-square' style='background-color: #00ff99;'>T0052</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0053'><span class='test-square' style='background-color: #ff9966;'>T0053</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0056'><span class='test-square' style='background-color: #ff6600;'>T0056</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0057'><span class='test-square' style='background-color: #cc6699;'>T0057</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0060'><span class='test-square' style='background-color: #ff3399;'>T0060</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0061'><span class='test-square' style='background-color: #9933ff;'>T0061</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0062'><span class='test-square' style='background-color: #cc6699;'>T0062</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0063'><span class='test-square' style='background-color: #99ccff;'>T0063</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0067'><span class='test-square' style='background-color: #33ff66;'>T0067</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0068'><span class='test-square' style='background-color: #ff3300;'>T0068</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0069'><span class='test-square' style='background-color: #33ff66;'>T0069</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0070'><span class='test-square' style='background-color: #27ae60;'>T0070</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0071'><span class='test-square' style='background-color: #ff0099;'>T0071</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0072'><span class='test-square' style='background-color: #2ecc71;'>T0072</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0073'><span class='test-square' style='background-color: #2980b9;'>T0073</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0074'><span class='test-square' style='background-color: #ff9933;'>T0074</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0075'><span class='test-square' style='background-color: #7f8c8d;'>T0075</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0076'><span class='test-square' style='background-color: #ff3300;'>T0076</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0077'><span class='test-square' style='background-color: #e67e22;'>T0077</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0078'><span class='test-square' style='background-color: #ff0066;'>T0078</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0100'><span class='test-square' style='background-color: #ff9933;'>T0100</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0101'><span class='test-square' style='background-color: #ff6600;'>T0101</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0102'><span class='test-square' style='background-color: #ff3300;'>T0102</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0103'><span class='test-square' style='background-color: #ff3300;'>T0103</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0104'><span class='test-square' style='background-color: #3399ff;'>T0104</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0105'><span class='test-square' style='background-color: #00ccff;'>T0105</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0108'><span class='test-square' style='background-color: #c0392b;'>T0108</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0109'><span class='test-square' style='background-color: #ff5050;'>T0109</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0110'><span class='test-square' style='background-color: #6633ff;'>T0110</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0111'><span class='test-square' style='background-color: #99ff33;'>T0111</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0112'><span class='test-square' style='background-color: #3498db;'>T0112</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0113'><span class='test-square' style='background-color: #00ff99;'>T0113</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0114'><span class='test-square' style='background-color: #27ae60;'>T0114</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0115'><span class='test-square' style='background-color: #ccff00;'>T0115</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0116'><span class='test-square' style='background-color: #9966ff;'>T0116</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0117'><span class='test-square' style='background-color: #ff0099;'>T0117</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0118'><span class='test-square' style='background-color: #33ff66;'>T0118</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0119'><span class='test-square' style='background-color: #ff0066;'>T0119</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0124'><span class='test-square' style='background-color: #ff6699;'>T0124</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0125'><span class='test-square' style='background-color: #cc6699;'>T0125</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0126'><span class='test-square' style='background-color: #99ccff;'>T0126</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0196'><span class='test-square' style='background-color: #ff6600;'>T0196</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0197'><span class='test-square' style='background-color: #ff6600;'>T0197</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0198'><span class='test-square' style='background-color: #ffcc33;'>T0198</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-30/T0001'><span class='test-square' style='background-color: #ff0066;'>T0001</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0002'><span class='test-square' style='background-color: #ff3300;'>T0002</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0003'><span class='test-square' style='background-color: #ff33cc;'>T0003</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0193'><span class='test-square' style='background-color: #0099ff;'>T0193</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-30/T0004'><span class='test-square' style='background-color: #c0392b;'>T0004</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0005'><span class='test-square' style='background-color: #27ae60;'>T0005</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0006'><span class='test-square' style='background-color: #f39c12;'>T0006</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0194'><span class='test-square' style='background-color: #ff0066;'>T0194</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-30/T0066'><span class='test-square' style='background-color: #00ff99;'>T0066</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0160'><span class='test-square' style='background-color: #2c3e50;'>T0160</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0200'><span class='test-square' style='background-color: #ff5050;'>T0200</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-30/T0230'><span class='test-square' style='background-color: #e67e22;'>T0230</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-09-26</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-26/T0169'><span class='test-square' style='background-color: #ff3300;'>T0169</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0170'><span class='test-square' style='background-color: #ffcc33;'>T0170</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-26/T0177'><span class='test-square' style='background-color: #ccff00;'>T0177</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0178'><span class='test-square' style='background-color: #ff0066;'>T0178</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-26/T0171'><span class='test-square' style='background-color: #3498db;'>T0171</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0172'><span class='test-square' style='background-color: #ff0033;'>T0172</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0173'><span class='test-square' style='background-color: #3399ff;'>T0173</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0174'><span class='test-square' style='background-color: #3399ff;'>T0174</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0175'><span class='test-square' style='background-color: #ff6600;'>T0175</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0176'><span class='test-square' style='background-color: #1abc9c;'>T0176</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-26/T0179'><span class='test-square' style='background-color: #ff5733;'>T0179</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-26/T0180'><span class='test-square' style='background-color: #6699ff;'>T0180</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-09-25</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-25/T0035'><span class='test-square' style='background-color: #6699ff;'>T0035</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-25/T0095'><span class='test-square' style='background-color: #e74c3c;'>T0095</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-25/T0023'><span class='test-square' style='background-color: #33ffcc;'>T0023</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-25/T0159'><span class='test-square' style='background-color: #ff99cc;'>T0159</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-09-24</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-24/T0107'><span class='test-square' style='background-color: #c0392b;'>T0107</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0130'><span class='test-square' style='background-color: #99ff33;'>T0130</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-24/T0099'><span class='test-square' style='background-color: #f1c40f;'>T0099</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0120'><span class='test-square' style='background-color: #66ff33;'>T0120</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0132'><span class='test-square' style='background-color: #27ae60;'>T0132</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-24/T0117'><span class='test-square' style='background-color: #ff0099;'>T0117</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0125'><span class='test-square' style='background-color: #cc6699;'>T0125</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0134'><span class='test-square' style='background-color: #ffcc00;'>T0134</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-24/T0145'><span class='test-square' style='background-color: #00ccff;'>T0145</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0151'><span class='test-square' style='background-color: #ffcc00;'>T0151</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-24/T0162'><span class='test-square' style='background-color: #66ff33;'>T0162</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-09-02</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-09-02/T0066'><span class='test-square' style='background-color: #00ff99;'>T0066</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0143'><span class='test-square' style='background-color: #66ffff;'>T0143</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0144'><span class='test-square' style='background-color: #ff5733;'>T0144</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0145'><span class='test-square' style='background-color: #00ccff;'>T0145</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0146'><span class='test-square' style='background-color: #6699ff;'>T0146</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0147'><span class='test-square' style='background-color: #c0392b;'>T0147</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0148'><span class='test-square' style='background-color: #3498db;'>T0148</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0151'><span class='test-square' style='background-color: #ffcc00;'>T0151</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0152'><span class='test-square' style='background-color: #0099ff;'>T0152</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0155'><span class='test-square' style='background-color: #ff5733;'>T0155</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0159'><span class='test-square' style='background-color: #ff99cc;'>T0159</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0160'><span class='test-square' style='background-color: #2c3e50;'>T0160</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0161'><span class='test-square' style='background-color: #d35400;'>T0161</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0162'><span class='test-square' style='background-color: #66ff33;'>T0162</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0164'><span class='test-square' style='background-color: #ff0066;'>T0164</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0165'><span class='test-square' style='background-color: #ccff00;'>T0165</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0166'><span class='test-square' style='background-color: #9966ff;'>T0166</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0167'><span class='test-square' style='background-color: #ff5733;'>T0167</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-09-02/T0168'><span class='test-square' style='background-color: #ff0066;'>T0168</span></a>&nbsp;</td>
</tr>
<tr>
    <td>2025-08-27</td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-27/T0106'><span class='test-square' style='background-color: #ff6699;'>T0106</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-27/T0138'><span class='test-square' style='background-color: #ff0099;'>T0138</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-27/T0139'><span class='test-square' style='background-color: #9933ff;'>T0139</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-27/T0140'><span class='test-square' style='background-color: #3399ff;'>T0140</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-27/T0141'><span class='test-square' style='background-color: #ff5733;'>T0141</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-27/T0137'><span class='test-square' style='background-color: #6699ff;'>T0137</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-27/T0136'><span class='test-square' style='background-color: #99ff33;'>T0136</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-08-20</td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-20/T0133'><span class='test-square' style='background-color: #ff5050;'>T0133</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-20/T0134'><span class='test-square' style='background-color: #ffcc00;'>T0134</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-20/T0135'><span class='test-square' style='background-color: #cc6699;'>T0135</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-20/T0136'><span class='test-square' style='background-color: #99ff33;'>T0136</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-08-14</td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-14/T0127'><span class='test-square' style='background-color: #2980b9;'>T0127</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-14/T0128'><span class='test-square' style='background-color: #f39c12;'>T0128</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-14/T0129'><span class='test-square' style='background-color: #c0392b;'>T0129</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-14/T0130'><span class='test-square' style='background-color: #99ff33;'>T0130</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-14/T0131'><span class='test-square' style='background-color: #2ecc71;'>T0131</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-14/T0132'><span class='test-square' style='background-color: #27ae60;'>T0132</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-14/T0124'><span class='test-square' style='background-color: #ff6699;'>T0124</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-14/T0125'><span class='test-square' style='background-color: #cc6699;'>T0125</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-14/T0126'><span class='test-square' style='background-color: #99ccff;'>T0126</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-08-13</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-13/T0120'><span class='test-square' style='background-color: #66ff33;'>T0120</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0121'><span class='test-square' style='background-color: #7f8c8d;'>T0121</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0122'><span class='test-square' style='background-color: #9b59b6;'>T0122</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0123'><span class='test-square' style='background-color: #ff6699;'>T0123</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-08-13/T0108'><span class='test-square' style='background-color: #c0392b;'>T0108</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0109'><span class='test-square' style='background-color: #ff5050;'>T0109</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0110'><span class='test-square' style='background-color: #6633ff;'>T0110</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0111'><span class='test-square' style='background-color: #99ff33;'>T0111</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0112'><span class='test-square' style='background-color: #3498db;'>T0112</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0113'><span class='test-square' style='background-color: #00ff99;'>T0113</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0114'><span class='test-square' style='background-color: #27ae60;'>T0114</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0115'><span class='test-square' style='background-color: #ccff00;'>T0115</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0116'><span class='test-square' style='background-color: #9966ff;'>T0116</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0117'><span class='test-square' style='background-color: #ff0099;'>T0117</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0118'><span class='test-square' style='background-color: #33ff66;'>T0118</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-08-13/T0119'><span class='test-square' style='background-color: #ff0066;'>T0119</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-05-23</td>
    <td><a href='/humanities_data_benchmark/archive/2025-05-23/T0106'><span class='test-square' style='background-color: #ff6699;'>T0106</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0107'><span class='test-square' style='background-color: #c0392b;'>T0107</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-05-23/T0098'><span class='test-square' style='background-color: #00ccff;'>T0098</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0099'><span class='test-square' style='background-color: #f1c40f;'>T0099</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-05-23/T0100'><span class='test-square' style='background-color: #ff9933;'>T0100</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0101'><span class='test-square' style='background-color: #ff6600;'>T0101</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0102'><span class='test-square' style='background-color: #ff3300;'>T0102</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0103'><span class='test-square' style='background-color: #ff3300;'>T0103</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0104'><span class='test-square' style='background-color: #3399ff;'>T0104</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-23/T0105'><span class='test-square' style='background-color: #00ccff;'>T0105</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-05-09</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-05-09/T0022'><span class='test-square' style='background-color: #99ff33;'>T0022</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0079'><span class='test-square' style='background-color: #00ff66;'>T0079</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0080'><span class='test-square' style='background-color: #9933ff;'>T0080</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0081'><span class='test-square' style='background-color: #7f8c8d;'>T0081</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0082'><span class='test-square' style='background-color: #ff0099;'>T0082</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0083'><span class='test-square' style='background-color: #2980b9;'>T0083</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0084'><span class='test-square' style='background-color: #66cc99;'>T0084</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0085'><span class='test-square' style='background-color: #8e44ad;'>T0085</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0086'><span class='test-square' style='background-color: #66ff33;'>T0086</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0087'><span class='test-square' style='background-color: #ff5050;'>T0087</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0088'><span class='test-square' style='background-color: #cc33ff;'>T0088</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0089'><span class='test-square' style='background-color: #2c3e50;'>T0089</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0090'><span class='test-square' style='background-color: #ff6699;'>T0090</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0091'><span class='test-square' style='background-color: #e74c3c;'>T0091</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0092'><span class='test-square' style='background-color: #0099ff;'>T0092</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0093'><span class='test-square' style='background-color: #ff5733;'>T0093</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0094'><span class='test-square' style='background-color: #0099ff;'>T0094</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0095'><span class='test-square' style='background-color: #e74c3c;'>T0095</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0096'><span class='test-square' style='background-color: #cc6699;'>T0096</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-09/T0097'><span class='test-square' style='background-color: #ff3399;'>T0097</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-05-07</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-05-07/T0022'><span class='test-square' style='background-color: #99ff33;'>T0022</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0079'><span class='test-square' style='background-color: #00ff66;'>T0079</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0080'><span class='test-square' style='background-color: #9933ff;'>T0080</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0081'><span class='test-square' style='background-color: #7f8c8d;'>T0081</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0082'><span class='test-square' style='background-color: #ff0099;'>T0082</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0083'><span class='test-square' style='background-color: #2980b9;'>T0083</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0084'><span class='test-square' style='background-color: #66cc99;'>T0084</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0085'><span class='test-square' style='background-color: #8e44ad;'>T0085</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0086'><span class='test-square' style='background-color: #66ff33;'>T0086</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0087'><span class='test-square' style='background-color: #ff5050;'>T0087</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0088'><span class='test-square' style='background-color: #cc33ff;'>T0088</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0089'><span class='test-square' style='background-color: #2c3e50;'>T0089</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0090'><span class='test-square' style='background-color: #ff6699;'>T0090</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0091'><span class='test-square' style='background-color: #e74c3c;'>T0091</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0092'><span class='test-square' style='background-color: #0099ff;'>T0092</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0093'><span class='test-square' style='background-color: #ff5733;'>T0093</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0094'><span class='test-square' style='background-color: #0099ff;'>T0094</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0095'><span class='test-square' style='background-color: #e74c3c;'>T0095</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0096'><span class='test-square' style='background-color: #cc6699;'>T0096</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-05-07/T0097'><span class='test-square' style='background-color: #ff3399;'>T0097</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-17</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-17/T0067'><span class='test-square' style='background-color: #33ff66;'>T0067</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0068'><span class='test-square' style='background-color: #ff3300;'>T0068</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0069'><span class='test-square' style='background-color: #33ff66;'>T0069</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0070'><span class='test-square' style='background-color: #27ae60;'>T0070</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0071'><span class='test-square' style='background-color: #ff0099;'>T0071</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0072'><span class='test-square' style='background-color: #2ecc71;'>T0072</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0073'><span class='test-square' style='background-color: #2980b9;'>T0073</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0074'><span class='test-square' style='background-color: #ff9933;'>T0074</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0075'><span class='test-square' style='background-color: #7f8c8d;'>T0075</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0076'><span class='test-square' style='background-color: #ff3300;'>T0076</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0077'><span class='test-square' style='background-color: #e67e22;'>T0077</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-17/T0078'><span class='test-square' style='background-color: #ff0066;'>T0078</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-11</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-11/T0010'><span class='test-square' style='background-color: #99ff33;'>T0010</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0011'><span class='test-square' style='background-color: #33ccff;'>T0011</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0012'><span class='test-square' style='background-color: #ff6600;'>T0012</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0013'><span class='test-square' style='background-color: #0099ff;'>T0013</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0014'><span class='test-square' style='background-color: #7f8c8d;'>T0014</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0015'><span class='test-square' style='background-color: #cc33ff;'>T0015</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0016'><span class='test-square' style='background-color: #33ccff;'>T0016</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0017'><span class='test-square' style='background-color: #ff6600;'>T0017</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0018'><span class='test-square' style='background-color: #ff9966;'>T0018</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0020'><span class='test-square' style='background-color: #16a085;'>T0020</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0023'><span class='test-square' style='background-color: #33ffcc;'>T0023</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0024'><span class='test-square' style='background-color: #ff33cc;'>T0024</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0025'><span class='test-square' style='background-color: #33ff66;'>T0025</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0036'><span class='test-square' style='background-color: #ff6600;'>T0036</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0038'><span class='test-square' style='background-color: #ff9966;'>T0038</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0039'><span class='test-square' style='background-color: #66cc99;'>T0039</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0040'><span class='test-square' style='background-color: #34495e;'>T0040</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0041'><span class='test-square' style='background-color: #33ffcc;'>T0041</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0042'><span class='test-square' style='background-color: #c0392b;'>T0042</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0043'><span class='test-square' style='background-color: #00ffcc;'>T0043</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0044'><span class='test-square' style='background-color: #ff5733;'>T0044</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0045'><span class='test-square' style='background-color: #16a085;'>T0045</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0048'><span class='test-square' style='background-color: #66ff33;'>T0048</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0049'><span class='test-square' style='background-color: #ff33cc;'>T0049</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0052'><span class='test-square' style='background-color: #00ff99;'>T0052</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0053'><span class='test-square' style='background-color: #ff9966;'>T0053</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0056'><span class='test-square' style='background-color: #ff6600;'>T0056</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0057'><span class='test-square' style='background-color: #cc6699;'>T0057</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0060'><span class='test-square' style='background-color: #ff3399;'>T0060</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0061'><span class='test-square' style='background-color: #9933ff;'>T0061</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0062'><span class='test-square' style='background-color: #cc6699;'>T0062</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-11/T0063'><span class='test-square' style='background-color: #99ccff;'>T0063</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-08</td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-08/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0008'><span class='test-square' style='background-color: #ffcc00;'>T0008</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0009'><span class='test-square' style='background-color: #f39c12;'>T0009</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0026'><span class='test-square' style='background-color: #6633ff;'>T0026</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0027'><span class='test-square' style='background-color: #ff9966;'>T0027</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0029'><span class='test-square' style='background-color: #ff6699;'>T0029</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0030'><span class='test-square' style='background-color: #3399ff;'>T0030</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0031'><span class='test-square' style='background-color: #ff0099;'>T0031</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0033'><span class='test-square' style='background-color: #f39c12;'>T0033</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-08/T0035'><span class='test-square' style='background-color: #6699ff;'>T0035</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-07</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-07/T0017'><span class='test-square' style='background-color: #ff6600;'>T0017</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-07/T0024'><span class='test-square' style='background-color: #ff33cc;'>T0024</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-07/T0025'><span class='test-square' style='background-color: #33ff66;'>T0025</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-02</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-02/T0022'><span class='test-square' style='background-color: #99ff33;'>T0022</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-02/T0023'><span class='test-square' style='background-color: #33ffcc;'>T0023</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-04-01</td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-01/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0008'><span class='test-square' style='background-color: #ffcc00;'>T0008</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0009'><span class='test-square' style='background-color: #f39c12;'>T0009</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-01/T0010'><span class='test-square' style='background-color: #99ff33;'>T0010</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0011'><span class='test-square' style='background-color: #33ccff;'>T0011</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0012'><span class='test-square' style='background-color: #ff6600;'>T0012</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0013'><span class='test-square' style='background-color: #0099ff;'>T0013</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0014'><span class='test-square' style='background-color: #7f8c8d;'>T0014</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0015'><span class='test-square' style='background-color: #cc33ff;'>T0015</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0016'><span class='test-square' style='background-color: #33ccff;'>T0016</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0017'><span class='test-square' style='background-color: #ff6600;'>T0017</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0018'><span class='test-square' style='background-color: #ff9966;'>T0018</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0019'><span class='test-square' style='background-color: #ff5733;'>T0019</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0020'><span class='test-square' style='background-color: #16a085;'>T0020</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0021'><span class='test-square' style='background-color: #ff3300;'>T0021</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-01/T0001'><span class='test-square' style='background-color: #ff0066;'>T0001</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0002'><span class='test-square' style='background-color: #ff3300;'>T0002</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0003'><span class='test-square' style='background-color: #ff33cc;'>T0003</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-04-01/T0004'><span class='test-square' style='background-color: #c0392b;'>T0004</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0005'><span class='test-square' style='background-color: #27ae60;'>T0005</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-04-01/T0006'><span class='test-square' style='background-color: #f39c12;'>T0006</span></a>&nbsp;</td>
    <td></td>
</tr>
<tr>
    <td>2025-03-05</td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-05/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0008'><span class='test-square' style='background-color: #ffcc00;'>T0008</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0009'><span class='test-square' style='background-color: #f39c12;'>T0009</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-05/T0010'><span class='test-square' style='background-color: #99ff33;'>T0010</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0011'><span class='test-square' style='background-color: #33ccff;'>T0011</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0012'><span class='test-square' style='background-color: #ff6600;'>T0012</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0013'><span class='test-square' style='background-color: #0099ff;'>T0013</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0014'><span class='test-square' style='background-color: #7f8c8d;'>T0014</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0015'><span class='test-square' style='background-color: #cc33ff;'>T0015</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0016'><span class='test-square' style='background-color: #33ccff;'>T0016</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0017'><span class='test-square' style='background-color: #ff6600;'>T0017</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0018'><span class='test-square' style='background-color: #ff9966;'>T0018</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-05/T0001'><span class='test-square' style='background-color: #ff0066;'>T0001</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0002'><span class='test-square' style='background-color: #ff3300;'>T0002</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0003'><span class='test-square' style='background-color: #ff33cc;'>T0003</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-05/T0004'><span class='test-square' style='background-color: #c0392b;'>T0004</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0005'><span class='test-square' style='background-color: #27ae60;'>T0005</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-05/T0006'><span class='test-square' style='background-color: #f39c12;'>T0006</span></a>&nbsp;</td>
    <td></td>
</tr>
<tr>
    <td>2025-03-04</td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-04/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-04/T0001'><span class='test-square' style='background-color: #ff0066;'>T0001</span></a>&nbsp;</td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>2025-03-02</td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-02/T0007'><span class='test-square' style='background-color: #66cc99;'>T0007</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-02/T0008'><span class='test-square' style='background-color: #ffcc00;'>T0008</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-02/T0009'><span class='test-square' style='background-color: #f39c12;'>T0009</span></a>&nbsp;</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-02/T0006'><span class='test-square' style='background-color: #f39c12;'>T0006</span></a>&nbsp;</td>
    <td></td>
</tr>
<tr>
    <td>2025-03-01</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-01/T0001'><span class='test-square' style='background-color: #ff0066;'>T0001</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-01/T0002'><span class='test-square' style='background-color: #ff3300;'>T0002</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-01/T0003'><span class='test-square' style='background-color: #ff33cc;'>T0003</span></a>&nbsp;</td>
    <td><a href='/humanities_data_benchmark/archive/2025-03-01/T0004'><span class='test-square' style='background-color: #c0392b;'>T0004</span></a>&nbsp;<a href='/humanities_data_benchmark/archive/2025-03-01/T0005'><span class='test-square' style='background-color: #27ae60;'>T0005</span></a>&nbsp;</td>
    <td></td>
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
