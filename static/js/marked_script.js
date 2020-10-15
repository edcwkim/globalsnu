$("h1.md2html").html($(".page-form #id_title").val());
$(".page-form #id_title").on("keypress input", function() {
  $("h1.md2html").html($(this).val());
});

var renderer = new marked.Renderer();
renderer.heading = function(text, level) {
  level = (level + 1).toString();
  return "<h" + level + ">" + text + "</h" + level + ">";
};

var options = {
  renderer: renderer,
  breaks: true,
  sanitize: true
};

$("div.md2html").html(marked($(".page-form #id_content").val(), options));
$(".page-form #id_content").on("keypress input", function() {
  $("div.md2html").html(marked($(this).val(), options));
});
