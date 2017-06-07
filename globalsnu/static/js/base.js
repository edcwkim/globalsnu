function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var Autocomplete = function(options) {
  this.url = options.url;
  this.input_box = $(options.input_selector);
  this.extra_text = options.extra_text;
  this.none_text = options.none_text;
  this.fetch_url = options.fetch_url;
  this.click = options.click;
};

Autocomplete.prototype.watch = function() {
  var self = this;
  // Watch the input box.
  self.input_box.on("input", function() {
    if ($(this).val()) {
      $.ajax({
        url: self.url,
        data: {'q': $(this).val(), 'fetch_url': self.fetch_url},
        success: function(data) {
          // Remove any existing results.
          $(".ac-results").remove();
          self.update_results(data);
          self.click();
        }
      });
    }
    else {
      // Remove any existing results.
      $(".ac-results").remove();
    }
  });
};

Autocomplete.prototype.update_results = function(data) {
  var results = data.results || [],
      results_wrapper = $("<div class='ac-results'></div>"),
      elem;

  if (results.length > 0) {
    for (var i in results) {
      elem = $("<div></div>")
        .addClass("ac-result")
        .text(results[i].name)
        .appendTo(results_wrapper);
    }
    if (!data.exists) {
      elem = $("<div></div>")
        .addClass("ac-result extra")
        .text(this.extra_text)
        .appendTo(results_wrapper);
    }
  }
  else {
    elem = $("<div></div>")
      .addClass("ac-result none")
      .text(this.none_text)
      .appendTo(results_wrapper);
  }
  this.input_box.after(results_wrapper);
};

function homeReady() {
  $(".navigator-form").submit(function(e) {
    e.preventDefault();
    var data = $(this).serialize(),
        idx = data.indexOf("&");
    if (idx >= 0) {
      var continent = 0,
          country = 0,
          language = 0,
          major = 0;
      data = data.replace(/&continent=/g, function(x) {
        ++continent;
        return (continent > 1) ? "," : x;
      });
      data = data.replace(/&country=/g, function(x) {
        ++country;
        return (country > 1) ? "," : x;
      });
      data = data.replace(/&language=/g, function(x) {
        ++language;
        return (language > 1) ? "," : x;
      });
      data = data.replace(/&major=/g, function(x) {
        ++major;
        return (major > 1) ? "," : x;
      });
      data = data.replace(data.substring(0, idx + 1), "");
      location.href = "/school/search/?" + data;
    }
    else
      alert("대륙, 국가, 언어, 전공 중 하나 이상을 선택해 주세요.");
  });

  var $continents = $("[id|=continent]");

  if ($("html").hasClass("full")) {
    $continents.change(function() {
      var hidden = 0;
      for (i = 0; i < $continents.length; ++i) {
        var code = $($continents[i]).data("code"),
            $object = $("input[data-continent-code="+ code + "]").closest("li");
        if ($continents[i].checked) {
          $object.show();
        }
        else {
          $object.hide();
          hidden += 1;
        }
      }
      if (hidden == $continents.length)
        $("input[data-continent-code]").closest("li").show();
    });

    $(".selector").click(function(e) {
      $(this).removeClass("masked")
             .addClass("unmasked")
             .css("overflow-y", "auto");
    });
    $(".selector .revert").click(function(e) {
      var $selector = $(this).closest(".selector");
      setTimeout(function() {
        $selector.css("overflow-y", "hidden")
                 .removeClass("unmasked")
                 .addClass("masked")
                 .find("input").prop("checked", false);
      }, 5);
    });

    $(".search-trigger").click(function(e) {
      $(".navigator-wrapper").addClass("search-show");
    });

    $(".search-trigger .revert").click(function(e) {
      setTimeout(function() {
        $(".navigator-wrapper").removeClass("search-show");
        $(".search-trigger input").val("");
      }, 5);
    });

    $(".manual-slide").click(function(e) {
      e.preventDefault();
      var hash = this.hash;
      $("html, body").animate({
        'scrollTop': $(hash).offset().top
      }, 800);
      window.location.hash = hash;
    });

    $("#manual .manual-wrapper .manual-nav li.first").closest("a").click(function(e) {
      e.preventDefault();
      $("html, body").animate({
        'scrollTop': $("#manual").offset().top
      }, 400);
      window.location.hash = "#manual";
    });

    $("#manual .manual-wrapper .things li a").click(function() {
      var $show_this = $("#" + $(this).data("show"));
      if ($show_this.hasClass("thing-left"))
        $("#manual .manual-wrapper .thing.thing-left.show").removeClass("show");
      else if ($show_this.hasClass("thing-right"))
      $("#manual .manual-wrapper .thing.thing-right.show").removeClass("show");
      $show_this.addClass("show");
    });
  }

  if ($("html").hasClass("mobile")) {
    $(".iscroll li.objects").each(function() {
      if ($(this).children().length === 0)
        $(this).remove();
    });

    var iscroll = new Array(4);
    $(".selector.iscroll-wrapper").each(function(idx) {
      var $li = $(this).find("li"),
          width = Math.max(165 * $li.length + 45, window.innerWidth + 90);
      $(this).find(".iscroll").width(width);
      iscroll[idx] = new IScroll(this, {
        eventPassthrough: true,
        scrollX: true,
        scrollY: false
      });
      iscroll[idx].disable();
    });

    $(".selector input").prop("disabled", true);

    $(".selector .mask").click(function() {
      var $wrapper = $(this).closest(".selector.iscroll-wrapper"),
          idx = $(".selector.iscroll-wrapper").index($wrapper[0]);
      $wrapper.toggleClass("selected");
      if ($wrapper.hasClass("selected")) {
        iscroll[idx].enable();
        iscroll[idx].scrollTo(-90, 0, 800, IScroll.utils.ease.bounce);
        $wrapper.find(".object:not(.disabled) input").prop("disabled", false);
      }
      else {
        iscroll[idx].scrollTo(0, 0, 1200, IScroll.utils.ease.elastic);
        iscroll[idx].disable();
        $wrapper.find("input").prop("checked", false)
                              .prop("disabled", true);
        if (idx === 0)
          $($(".selector")[1]).find(".object").removeClass("disabled")
                                              .find("input").prop("disabled", false);
      }
    });

    $(".selector .objects").click(function(e) {
      var $wrapper = $(this).closest(".selector.iscroll-wrapper"),
          idx = $(".selector.iscroll-wrapper").index($wrapper[0]);
      if (!$wrapper.hasClass("selected")) {
        e.preventDefault();
        $wrapper.addClass("selected");
        iscroll[idx].enable();
        iscroll[idx].scrollTo(-90, 0, 800, IScroll.utils.ease.bounce);
        $wrapper.find(".object:not(.disabled) input").prop("disabled", false);
      }
    });

    $continents.change(function() {
      var hidden = 0;
      for (i = 0; i < $continents.length; ++i) {
        var code = $($continents[i]).data("code"),
            $object = $("input[data-continent-code="+ code + "]").closest(".object");
        if ($continents[i].checked) {
          $object.removeClass("disabled")
                 .find("input").prop("disabled", false);
        }
        else {
          $object.addClass("disabled")
                 .find("input").prop("disabled", true);
          hidden += 1;
        }
      }
      if (hidden == $continents.length)
        $("input[data-continent-code]").closest(".object").removeClass("disabled")
                                                          .find("input").prop("disabled", false);
    });

    $(".shortcut .iscroll-wrapper").each(function() {
      var $li = $(this).find("li"),
          width = $li.length * $li.outerWidth() + 60;
      $(this).find(".iscroll").width(width);
      new IScroll(this, {
        eventPassthrough: true,
        scrollX: true,
        scrollY: false
      });
    });
  }
}

function parseIntThenAdd($obj, x) {
  var newInt = +$obj.text().replace(",", "") + x;
  return $obj.text(newInt.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
}

$(function() {
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain)
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });

  new Autocomplete({
    url: '/autocomplete/tag/',
    input_selector: '.ac-tag',
    extra_text: '태그 등록하기',
    none_text: '태그 등록하기',
    fetch_url: false,
    click: function() {
      var $wrapper = $(".tag-wrapper");
      $wrapper.find(".ac-result").click(function() {
        var name, $last, $results = $(this).parent(".ac-results").hide();

        if ($(this).hasClass("extra") || $(this).hasClass("none"))
          name = $results.siblings("input").val();
        else
          name = $(this).text();

        if ($wrapper.find(".empty").length) {
          $last = $wrapper.find(".empty")
                          .hide();
        }
        else
          $last = $(".tag").last();

        $("<span class='tag'>#<span class='name'>" + name + "</span> <span class='remove'></span></span>").insertAfter($last);
        $results.siblings("input").val("");

        $(".tag .remove").click(function() {
          var $tag = $(this).closest(".tag"),
              name = $tag.find(".name").text();
          $tag.hide();
          $.ajax({
            type: "POST",
            data: {'school': true, 'tag_name': name, 'action': 'remove'},
            datatype: "json",
            error: function(response) {
              $tag.show();
            }
          });
        });

        $.ajax({
          type: "POST",
          data: {'school': true, 'tag_name': name, 'action': "add"},
          error: function(data) {
            alert("Something went wrong :(");
          }
        });
      });
    }
  }).watch();

  /*
  if ($("nav").hasClass("mobile")) {
    $(window).scroll(function() {
      if ($(this).scrollTop() > 0)
        $(".navbar").addClass("scrolled");
      else
        $(".navbar").removeClass("scrolled");
    });
  }
  */
  $(".hamburger").click(function() {
    $("nav").toggleClass("expanded");
    $("html, body").toggleClass("modal-open");
  });

  if ($("nav").hasClass("navbar-public")) {
    var offset;
    $(window).scroll(function() {
      if ($("body > .about").length)
        offset = $(".about #general").offset().top;
      else
        offset = $(".container > .logo").height();
      if ($(this).scrollTop() > offset)
        $(".navbar-public").addClass("scrolled");
      else
        $(".navbar-public").removeClass("scrolled");
    });
  }

  $(".about .down").click(function(e) {
    e.preventDefault();
    var hash = this.hash;
    $("html, body").animate({
      'scrollTop': $(hash).offset().top + 1
    }, 800);
    window.location.hash = hash;
  });

  $(".popup").click(function() {
    $(this).fadeOut("fast");
  });

  $(".event-button").click(function() {
    $(".event-popup").fadeIn("fast");
  });

  $(".login-register").click(function(event) {
    event.preventDefault();
    window.history.pushState("", "", "/register/");
    $(".landing-wrapper").removeClass("login")
                         .addClass("register transition");
    window.onpopstate = function() {
      var pathname = window.location.pathname;
      if (pathname == "/" || pathname.lastIndexOf("/?", 0) === 0)
        $(".landing-wrapper").removeClass("register")
                             .addClass("login");
    };
  });

  $(".register-login").click(function(event) {
    event.preventDefault();
    window.history.pushState("", "", "/");
    $(".landing-wrapper").removeClass("register")
                         .addClass("login transition");
    window.onpopstate = function() {
      var pathname = window.location.pathname;
      if (pathname.lastIndexOf("/register", 0) === 0)
        $(".landing-wrapper").removeClass("login")
                             .addClass("register");
    };
  });

  $(".register-form").submit(function(event) {
    event.preventDefault();
    $.ajax({
      url: $(this).attr("action"),
      type: "POST",
      data: $(this).serialize(),
      success: function(response) {
        window.history.pushState("", "", "/register/verify/");
        $(".yellow-container > *").remove();
        $(".landing-wrapper").addClass("verify");
        var response_html = $(response).find(".register-input-set > *");
        $(".register-input-set").html(response_html);
      },
      error: function(response) {
        var json = JSON.parse(response.responseText);
        for (var key in json)
          alert(json[key]);
      }
    });
  });

  homeReady();

  $(".tag-wrapper .trigger").click(function() {
    $(this).closest(".tag-wrapper").toggleClass("edit");
  });

  $(".tag .remove").click(function() {
    var $tag = $(this).closest(".tag"),
        name = $tag.find(".name").text();
    $tag.hide();
    $.ajax({
      type: "POST",
      data: {'school': true, 'tag_name': name, 'action': 'remove'},
      datatype: "json",
      error: function(response) {
        $tag.show();
      }
    });
  });

  $(".page-wrapper .like").click(function() {
    var $this = $(this);
    $this.toggleClass("liked");
    $("body").toggleClass("nav-heart-red");
    $.ajax({
      type: "POST",
      data: {'school': true, 'like': true},
      dataType: "json",
      error: function(response) {
        $this.toggleClass("liked");
        $("body").toggleClass("nav-heart-red");
      }
    });
  });

  $(".essay-detail .like").click(function() {
    var $this = $(this);
    $this.toggleClass("liked");
    $("body").toggleClass("nav-heart-red");
    $.ajax({
      type: "POST",
      url: $this.data("action"),
      data: {},
      dataType: "json",
      error: function(response) {
        $this.toggleClass("liked");
        $("body").toggleClass("nav-heart-red");
      }
    });
  });

  /*
  $(".star-wrapper.user > .star-0").click(function() {
    $(".star-wrapper.user").removeClass("rated");
    $(".star-wrapper.user > :nth-child(n)").removeClass("filled");
    $.ajax({
      type: "POST",
      data: {'school': true, 'rate': 0},
      datatype: "json"
    });
  });
  var starEnter = function(e) {
    $(".star-wrapper.user:not(.rated) > :nth-child(n)").addClass("filled");
    $(".star-wrapper.user:not(.rated) > :nth-child(n" + parseInt(e.data.i + 2) + ")").removeClass("filled");
  };
  var starClick = function(e) {
    $(".star-wrapper.user").addClass("rated");
    $(".star-wrapper.user > :nth-child(n)").addClass("filled");
    $(".star-wrapper.user > :nth-child(n" + parseInt(e.data.i + 2) + ")").removeClass("filled");
    $.ajax({
      type: "POST",
      data: {'school': true, 'rate': e.data.i},
      datatype: "json",
      error: function(response) {
        $(".star-wrapper.user").removeClass("rated");
      }
    });
  };
  $(".star-wrapper.user > .star-1").mouseenter({i: 1}, starEnter)
                                        .click({i: 1}, starClick);
  $(".star-wrapper.user > .star-2").mouseenter({i: 2}, starEnter)
                                        .click({i: 2}, starClick);
  $(".star-wrapper.user > .star-3").mouseenter({i: 3}, starEnter)
                                        .click({i: 3}, starClick);
  $(".star-wrapper.user > .star-4").mouseenter({i: 4}, starEnter)
                                        .click({i: 4}, starClick);
  $(".star-wrapper.user > .star-5").mouseenter({i: 5}, starEnter)
                                        .click({i: 5}, starClick);
  $(".star-wrapper.user").mouseleave(function() {
    $(".star-wrapper.user:not(.rated) > :nth-child(n)").removeClass("filled");
  });
  */

  $("#overlay, .overlay-modal > button.close").click(function(e) {
    e.preventDefault();
    window.location.replace("#");
    if (typeof window.history.replaceState == 'function')
      window.history.replaceState({}, "", window.location.href.slice(0, -1));
  });

  $("#edit-country a").click(function(e) {
    $(this).data("id");
  });
});
