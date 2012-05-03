
$(document).ready(function() {
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