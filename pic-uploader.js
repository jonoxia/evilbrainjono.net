
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
		    id: i
                           });
    }
    previewFile();
  }

  function output(text) {
    document.getElementById("output").innerHTML = text;
  }

  function previewFile() {
    var nextFile = g_files[g_fileIndex];
    var imageType = /image.*/;
    if (!nextFile.type.match(imageType)) {  
      output("Not an image");
      return;
    }

    var metadata = g_file_metadata[g_fileIndex];
    var ctx = document.getElementById("preview-canvas").getContext("2d");

    function drawIt(metadata) {
	ctx.clearRect(0, 0, 600, 800);
        ctx.save();
        ctx.translate(300, 400);
	ctx.rotate(metadata.rotation * Math.PI / 2);
        ctx.scale(metadata.scale, metadata.scale);
        ctx.drawImage(metadata.img,
		      0 - metadata.width/2,
		      0 - metadata.height/2);
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

  function nextFile() {
    if (g_fileIndex >= g_files.length) {
      output("No more files to preview");
      return;
    }
    g_fileIndex ++;
    previewFile();
  }

  function previousFile() {
    if (g_fileIndex <= 0) {
      output("No previous files to preview");
      return;
    }
    g_fileIndex --;
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
    var canvas = document.getElementById("preview-canvas");    
    var picSet = document.getElementById("pic-set-name").value;


    // Client side TODOs: 
    // TODO set bounding box before doing toDataURL so we don't pick up whitespace
    // on the edges.
    // TODO allow user to set bounding box manually, as well as setting offset manually
    // TODO show status of all ongoing uploads while allowing user to move on to next
    // picture and start writing a caption there.
    // TODO why is it taking so long?
    var bbox = {};
    if (metadata.rotation == 1 || metadata.rotation == 3) {
	bbox.width = Math.floor( metadata.height * metadata.scale + 0.5);
	bbox.height = Math.floor( metadata.width * metadata.scale + 0.5);
    } else {
	bbox.width = Math.floor( metadata.width * metadata.scale + 0.5);
	bbox.height = Math.floor( metadata.height * metadata.scale + 0.5);
    }

    var dataUrl = canvas.toDataURL("image/jpg"); // will this throw exception?
    output("Uploading image and caption...");
    console.log(dataUrl);
    
    var postArgs = {
        filename: metadata.id,
        directory: picSet,
	caption: metadata.caption,
	altText: metadata.altText,
	width: bbox.width,
	height: bbox.height,
	img: dataUrl
    };

    jQuery.ajax({url:"pic-uploader.py",
		data: postArgs,
		type: "POST",
		success: function(data, textStatus) {
                  output("Success");
		  metadata.uploaded = true; // TODO use this to display
		                              //loaded msg
		  output(data);
	        },
		error: function(req, textStatus, error) {
                  output("Failed: " + error);
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
	case 107:
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
        }
      }
  }
  
document.addEventListener("keydown", handleKeypress, false);