
  var g_files;
  var g_fileIndex;
  var g_file_metadata = [];

  function handleFiles(files) {
    g_files = files;
    g_fileIndex = 0;
    for (var i = 0; i < files.length; i++) {
	g_file_metadata.push({ rotation: 0,
		    uploaded: false,
		    scale: 1.0,
		    altText: "",
		    caption: "",
		    img: null,
		    id: i,
		    offsetX: 0,
		    offsetY: 0
                           });
    }
    previewFile();
  }

  function output(text) {
    document.getElementById("output").innerHTML = text;
  }

  function drawFile(canvas) {
    var nextFile = g_files[g_fileIndex];
    var imageType = /image.*/;
    if (!nextFile.type.match(imageType)) {  
      output("Not an image");
      return;
    }

    var metadata = g_file_metadata[g_fileIndex];
    var ctx = canvas[0].getContext("2d");

    function drawIt(metadata) {
	ctx.clearRect(0, 0, 600, 800);
        ctx.save();
        ctx.translate(300, 400);
	ctx.translate(metadata.offsetX, metadata.offsetY);
	ctx.rotate(metadata.rotation * Math.PI / 2);
        ctx.translate(-300, -400);
        ctx.scale(metadata.scale, metadata.scale);
        ctx.drawImage(metadata.img, 0, 0);
	ctx.restore();
    }

    if (metadata.img) {
      drawIt(metadata);
      output("Image preview: ");
      output("Pic number: " + metadata.id);
    } else {
      output("Loading image file...");
      var reader = new FileReader();
      reader.onload = function(e) {
        var img = new Image();
        img.onload = function() {
	  metadata.width = parseInt(img.width);
	  metadata.height = parseInt(img.height);
	  metadata.img = img;
	  
	  metadata.scale = (600.0 / img.width);

	  drawIt(metadata);
	};
	img.src = e.target.result;
      };
      reader.readAsDataURL(nextFile);
    }
  }

function previewFile() {
    drawFile($("#preview-canvas"));
}

function deleteImage() {
    // Don't actually remove the image from g_files;
    // other code depends on the indexes to be stable.
    // Instead, mark its metadata as deleted and then
    // skip those when going through.
    g_file_metadata[g_fileIndex].deleted = true;

    // get rid of references to the picture data so the 
    // garbage collector can clean it up:
    g_files[g_fileIndex] = null;
    g_file_metadata[g_fileIndex].img = null;

    // move us to the next non-deleted image:
    nextFile();
}

  function nextFile() {
    var newIndex = g_fileIndex + 1;
    // skip deleted/uploaded pics:
    while (newIndex < g_files.length &&
	   (g_file_metadata[newIndex].deleted ||
	    g_file_metadata[newIndex].uploaded)) {
	newIndex ++;
    }
    // Don't go past the end:
    if (newIndex >= g_files.length) {
      output("No more files to preview");
      return;
    }
    g_fileIndex = newIndex;
    previewFile();
  }

  function previousFile() {
    var newIndex = g_fileIndex - 1;
    // skip deleted/uploaded pics:
    while (newIndex >= 0 &&
	   (g_file_metadata[newIndex].deleted ||
	    g_file_metadata[newIndex].uploaded)) {
	newIndex --;
    }
    // Don't go past the en
    if (newIndex < 0) {
      output("No previous files to preview");
      return;
    }
    g_fileIndex = newIndex;
    previewFile();
  }

  function saveText() {
    var metadata = g_file_metadata[g_fileIndex];
    metadata.altText = document.getElementById("alt-text").value;
    metadata.caption = document.getElementById("caption").value;
  }

  function restoreText() {
    var metadata = g_file_metadata[g_fileIndex];
    var altText = document.getElementById("alt-text");
    altText.value = metadata.altText;
    document.getElementById("caption").value = metadata.caption;
    altText.focus();
  }

  function rotatePreview() {
    var metadata = g_file_metadata[g_fileIndex];
    metadata.rotation += 1;
    if (metadata.rotation == 4) metadata.rotation = 0;
    if (metadata.rotation == 1 || metadata.rotation == 3) {
	metadata.scale = (600.0 / metadata.height);
    } else {
	metadata.scale = (600.0 / metadata.width);
    }
    previewFile();
  }

  function zoomInPreview() {
    var metadata = g_file_metadata[g_fileIndex];
    metadata.scale += 0.1;
    previewFile();
  }

  function zoomOutPreview() {
    var metadata = g_file_metadata[g_fileIndex];
    metadata.scale -= 0.1;
    previewFile();
  }

  function uploadImage() {
    output("Converting image...");
    var metadata = g_file_metadata[g_fileIndex];
    var picSet = document.getElementById("pic-set-name").value;

    metadata.altText = document.getElementById("alt-text").value;
    metadata.caption = document.getElementById("caption").value;

    // Client side TODOs: 
    // TODO set bounding box before doing toDataURL so we don't pick up whitespace
    // on the edges.
    // TODO allow user to set bounding box manually, as well as setting offset manually
    // TODO show status of all ongoing uploads while allowing user to move on to next
    // picture and start writing a caption there.
    // TODO why is it taking so long?
    // TODO it's picking up incorrect width and height properties for some reason.
    var bbox = {};
    if (metadata.rotation == 1 || metadata.rotation == 3) {
	bbox.width = Math.floor( metadata.height * metadata.scale + 0.5);
	bbox.height = Math.floor( metadata.width * metadata.scale + 0.5);
    } else {
	bbox.width = Math.floor( metadata.width * metadata.scale + 0.5);
	bbox.height = Math.floor( metadata.height * metadata.scale + 0.5);
    }
    console.log("width = " + bbox.width + ", height = " + bbox.height);
    
    var exportCanvas = $("<canvas></canvas>");
    exportCanvas.attr("width", bbox.width);
    exportCanvas.attr("height", bbox.height);
    $("#export-area").append(exportCanvas);
    drawFile(exportCanvas);
    var dataUrl = exportCanvas[0].toDataURL("image/jpg");
    $("#export-area").empty();

    var postArgs = {
        filename: metadata.id,
        directory: picSet,
	caption: metadata.caption,
	altText: metadata.altText,
	width: bbox.width,
	height: bbox.height,
	img: dataUrl
    };
    output("Uploading image and caption... " + postArgs.caption);
    var progressMeter = $("<li>Uploading image " + metadata.id + " ...</li>");
    $("#in-progress").append(progressMeter);

    jQuery.ajax({url:"pic-uploader.py",
		data: postArgs,
		type: "POST",
		success: function(data, textStatus) {
                  output(data);
		  metadata.uploaded = true; // TODO use this to display
		                              //loaded msg
		  progressMeter.remove();
	        },
		error: function(req, textStatus, error) {
                  output(error);
		  progressMeter.remove();
	        },
		dataType: "html"});    
    // TODO show progress bar.
  }

  function handleKeypress(e) {
      if (e.ctrlKey) {
        e.preventDefault();
        output("key pressed - " + e.which);

	switch(e.which) {
        // ctrl - N
	case 78:
          saveText();
          nextFile();
          restoreText();
	  break;
        // ctrl - P
	case 80:
          saveText();
          previousFile();
	  restoreText();
	  break;
	// ctrl - R
	case 82:
          rotatePreview();
	  break;
	  // ctrl - +
	case 107: case 61:
          zoomInPreview();
          break;
         // ctrl - -
	case 109:
          zoomOutPreview();
          break;
        // ctrl - S
        case 83: 
	  uploadImage();
	  break;
        // ctrol -X
	case 88:
	  deleteImage();
	  break;
        }
      }
  }

var mouseDownLoc = {x: 0, y: 0};
var mouseIsDown = false;

function canvasMouseDown(e) {
    mouseDownLoc.x = e.pageX;
    mouseDownLoc.y = e.pageY;
    mouseIsDown = true;
}

function canvasMouseMove(e) {
    if (mouseIsDown) {
    var dx = e.pageX - mouseDownLoc.x;
    var dy = e.pageY - mouseDownLoc.y;
    var metadata = g_file_metadata[g_fileIndex];
    metadata.offsetX += dx;
    metadata.offsetY += dy;
    previewFile();
    mouseDownLoc.x = e.pageX;
    mouseDownLoc.y = e.pageY;
    }
}

function canvasMouseUp(e) {
    mouseIsDown = false;
}

$(document).ready(function() {  
	$(document).bind("keydown", handleKeypress);
	$("#preview-canvas").bind("mousedown", canvasMouseDown);
	$("#preview-canvas").bind("mouseup", canvasMouseUp);
	$("#preview-canvas").bind("mousemove", canvasMouseMove);
    });

