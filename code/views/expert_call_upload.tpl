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
            <form action="/upload/expert_call" method="post" enctype="multipart/form-data">
                <table>
                <tr><td>
                    <label>选择上传文件类型：</label>
                </td></tr>
                <tr><td>
                    <label><input type="radio" name="type" value="data" /> 数据（有字段头）： </label></td>
                    <td><label>包含字段：日期,星期,科室名称,医生,时段,初诊,复诊 </label></td>
                    <tr><td></td><td>
                    <label>例如：4/1/2017,星期六,某某科,某某,上午,2,0 </label></td>
                </tr>
                <tr><td>
                    <label><input type="radio" name="type" value="rule" /> 规则（有字段头）： </label></td>
                    <td><label>包含字段：科室,姓名,出诊时间 </label></td>
                    <tr><td></td><td>
                    <label>例如：某某科,某某,周一上午、周三全天、周四下午 </label></td></tr>
                    <tr><td></td><td>
                    <label>例如：某某科,某某,2017.3.16-2017.4.25：周二全天、周三全天；2017.4.26-： </label></td></tr>
                </tr>
                <tr><td></td><td>
                    <input type="file" name="data" />
                </td></tr>
                </table>
                <input type="submit" value="上传" />
                <label><a href="/location"><button type="button"> 返回 </button></a></label>
            </form>
        </div>
    </div>
</body>
</html>
