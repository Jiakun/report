<!doctype html>
<html lang="zh">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>口院运营办统计工具</title>
	<link rel="stylesheet" type="text/css" href="assets/css/normalize.css" />
	<link rel="stylesheet" type="text/css" href="assets/css/default.css" />
	<style type="text/css">
		.demo-chat{width: 80%;margin: 0 auto;}
	</style>
	<!--[if IE]>
		<script src="http://libs.useso.com/js/html5shiv/3.7/html5shiv.min.js"></script>
	<![endif]-->
</head>
<body>
	<div class="htmleaf-container">
		<header class="htmleaf-header">
			<div class="htmleaf-demo center">
				<label><a href="/expert_call">专家出诊统计</a></label>
				<label><a href="/location">地域统计</a></label>
			</div>
		</header>

		<div class="htmleaf-content">
			<form action="/expert_call" method="post" target="_blank">
			<label><a href="/upload_expert_call">上传文件</a></label>
			<table>
			<tr><td>
                <label>开始日期：</label><input name="period_after" type="date" value="2017-01-01"/>
                </td>
                <td>
                <label>结束日期：</label><input name="period_before" type="date" value="2018-01-01"/>
                </td>
            <tr><td>
                <b> 规则文件数： {{rule_file_num}} </b>
            </td></tr>
                %for row in rule_list:
                    <tr>
                    <td><label><input type="radio" name="rule" value="{{row}}"/> {{row}} </label></td>
                    <td>
                        <label><button type="button" onclick="window.open('/download/expert_call/rule/{{row}}')"> 下载 </button></label>
                        <label><button type="button" onclick="window.open('/delete/expert_call/rule/{{row}}')" formtarget="_self"> 删除 </button></label>
                    </td>
                    </tr>
                %end
            <tr><td>
                <b> 数据文件数： {{data_file_num}} </b>
            </td></tr>
                %for row in data_list:
                    <tr>
                    <td><label><input type="radio" name="data" value="{{row}}"/> {{row}} </label></td>
                    <td>
                        <label><button type="button" onclick="window.open('/download/expert_call/data/{{row}}')"> 下载 </button></label>
                        <label><button type="button" onclick="window.open('/delete/expert_call/data/{{row}}')" formtarget="_self"> 删除 </button></label>
                    </td>
                    </tr>
                %end
            </table>
                <input type="submit" value="开始计算" />

            </form>

		</div>
</div>
</body>
</html>
