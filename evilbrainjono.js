var tagList = [];

// tag autocomplete function for when tagging posts
function suggestTags(e) {
    if (tagList.length == 0) {
	tagList = $("#hidden-tag-list").html().split(",");
    }
    var input = $("#tag-input").val();
    var inputTags = input.split(",");
    var lastTag = inputTags[ inputTags.length - 1 ].replace(" ", "");

    $("#tag-suggestions").empty();
    for (var x = 0; x < tagList.length; x ++) {
	if (tagList[x].indexOf(lastTag) > -1) {
	    $("#tag-suggestions").append(" " + tagList[x]);
	}
    }
}

function enableShowHideLinks(linkClass, divClass, hideText, showText) {
	var unfoldLinks = $(linkClass);
	var unfoldDivs = $(divClass);

	var unfoldStatus = [];

	var makeLinkHandler = function(link, div, index) {
            link.click(function(e) {
                if (unfoldStatus[index] == "hidden") {
                        div.slideDown();
                        link.html(hideText);
                        unfoldStatus[index] = "shown";
                    } else {
                        div.slideUp();
                        link.html(showText);
                        unfoldStatus[index] = "hidden";
		    }
		});
	};

	for (var i = 0; i < unfoldLinks.length; i++) {
	    // Initialize unfoldStatus array to correctly track
	    // whether the div started out shown or hidden:
	    if ($(unfoldDivs[i]).css("display") == "none") {
		unfoldStatus.push("hidden");
	    } else {
		unfoldStatus.push("shown");
	    }
	    makeLinkHandler($(unfoldLinks[i]), $(unfoldDivs[i]), i);
	}
}

$(document).ready(function() {
	// suggest tags when i type in the tag box
	$("#tag-input").keyup(suggestTags);
	// Add handlers for "read more" links on long posts
	enableShowHideLinks(".unfold-link", ".unfold-div", "Read Less", "Read More");
	// Add handlers for "show/hide comments" links:
	enableShowHideLinks(".comment-link", ".comments", "Hide Comments", "Show Comments");
});