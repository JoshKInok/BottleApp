% import os
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "xhtml11.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

<title>Highslide JS</title>
<script type="text/javascript" src="/static/js/highslide-with-gallery.js"></script>
<script type="text/javascript" src="/static/js/jquery-1.9.1.min.js"></script>
<script type="text/javascript" src="/static/js/jquery.unveil.min.js"></script>

<link rel="stylesheet" type="text/css" href="/static/css/highslide.css" />
<script type="text/javascript">
	hs.graphicsDir = '/static/graphics/';
	hs.align = 'center';
	hs.transitions = ['expand', 'crossfade'];
	hs.outlineType = 'rounded-white';
	hs.wrapperClassName = 'controls-in-heading';
	hs.fadeInOut = true;
	//hs.dimmingOpacity = 0.75;
	hs.numberOfImagesToPreload = 10000;


	// Add the controlbar
	if (hs.addSlideshow) hs.addSlideshow({
		//slideshowGroup: 'group1',
		interval: 5000,
		repeat: false,
		useControls: true,
		fixedControls: false,
		overlayOptions: {
			opacity: 1,
			position: 'top right',
			hideOnMouseOut: false
		}
	});
</script>

</head>
<body>
<div class="highslide-gallery">

% for image in image_list:
    % try:
        % _title = images_and_titles[image]
    % except KeyError:
        % _title = ""
    % end

    % image_path = os.path.join('image',root_dir,image)
    % thumb_path = os.path.join('image',root_dir,'thumbs',image)
    <a href="{{image_path}}" class="highslide" onclick="return hs.expand(this)">
	    <img src="/static/img/loader.gif" data-src="{{thumb_path}}" alt="Highslide JS"
		    title="Click to enlarge"/>
    </a>

    <div class="highslide-heading">
	    {{_title}}
    </div>

% end

</div>
<script>
$(document).ready(function() {
  $("img").unveil();
});
</script>
</body>
</html>