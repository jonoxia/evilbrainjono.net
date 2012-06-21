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


$(document).ready(function() {
	// suggest tags when i type in the tag box
	$("#tag-input").keyup(suggestTags);

	// Add handlers for "read more" links on long posts
	var unfoldLinks = $(".unfold-link");
	var unfoldDivs = $(".unfold-div");

	var unfoldStatus = [];

	var makeLinkHandler = function(link, div, index) {
            link.click(function(e) {
                if (unfoldStatus[index] == "hidden") {
                        div.slideDown();
                        link.html("Read Less");
                        unfoldStatus[index] = "shown";
                    } else {
                        div.slideUp();
                        link.html("Read More");
                        unfoldStatus[index] = "hidden";
		    }
		});
	};

	for (var i = 0; i < unfoldLinks.length; i++) {
	    unfoldStatus.push("hidden");
	    makeLinkHandler($(unfoldLinks[i]), $(unfoldDivs[i]), i);
	}
});