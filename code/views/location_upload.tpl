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
			<label><b>请上传{{title}}文件（.csv 格式）</b></label>
            <form action="/upload/location" method="post" enctype="multipart/form-data">
                <table>
                <tr><td>
                    <label>选择上传文件类型：</label>
                </td></tr>
                <tr><td>
                    <label><input type="radio" name="type" value="data" /> 数据（有字段头）： </label></td>
                    <td><label>包含字段：项目,人次,诊疗费,省市 </label></td>
                    <tr><td></td><td>
                    <label>例如：北京海淀区,10000,1000000,北京 </label></td></tr>
                    <tr><td></td><td>
                    <label>省市项中除中国省市外，必须填写“其他来源不明”或“其他外籍”。</label>
                    <p>严格安装输入格式，不能包含其他数据，如求和值等 </p></td></tr>
                <tr><td></td><td>
                    <input type="file" name="data" />
                </td></tr>
                </table>
                <input type="submit" value="上传" /></td></tr>
                <label><a href="/location"><button type="button"> 返回 </button></a></label>
            </form>
		</div>
</div>
</body>
</html>
