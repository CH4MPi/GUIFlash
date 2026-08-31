package net.gambiter.components
{
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.AntiAliasType;
	import flash.text.TextFieldAutoSize;

	import flash.display.Sprite;
	import flash.display.LineScaleMode;
	import flash.display.CapsStyle;
	import flash.display.JointStyle;
	
	import net.gambiter.FlashUI;
	import net.gambiter.utils.Align;
	import net.gambiter.utils.Properties;
	import net.gambiter.core.UIComponentEx;
	
	public class LabelEx extends UIComponentEx
	{
		public static const NAME_FONT:String = "$FieldFont";
		
		private var textField:TextField;
		private var customBG:Sprite;
		
		private var _text:String;
		private var _isHtml:Boolean;
		private var _hAlign:String;
		private var _vAlign:String;

		// new custom background
		private var bg_alpha:Number;
		private var	bg_border:Boolean;
		private var bg_borderColor:uint;
		private var bg_caps:String;
		private var bg_color:uint;
		private var bg_ellipseWidth:Number;
		private var bg_fill:Boolean;
		private var bg_joints:String;
		private var bg_margin:Number;
		private var bg_miterLimit:Number;
		private var bg_pixelHinting:Boolean;
		private var bg_scaleMode:String;
		private var bg_thickness:Number;
		// !new custom background
		
		public function LabelEx()
		{
			super();
			
			textField = new TextField();
			textField.name = "label";
//			addChild(textField);

			_isHtml = true;			
			_hAlign = Align.LEFT;
			_vAlign = Align.TOP;
			
			textField.width = 0;
			textField.height = 0;

			textField.mouseEnabled = false;
						
			textField.wordWrap = false;
			textField.multiline = false;
			textField.selectable = false;
			textField.background = false;
			textField.backgroundColor = 0x000000;
			
			textField.embedFonts = true;
			textField.autoSize = TextFieldAutoSize.LEFT;
			textField.antiAliasType = AntiAliasType.ADVANCED;
			
			textField.defaultTextFormat = new TextFormat(NAME_FONT, 12, 0xFFFFFF, false, false, false, "", "", "left", 0, 0, 0, 0);
			Properties.setShadow(textField, {
				"distance": 4,
				"angle": 45,
				"color": 0x999999,
				"alpha": 1,
				"blurX": 4,
				"blurY": 4,
				"strength": 1,
				"quality": 1
			});
			addChild(textField);
		}
		
		override protected function configUI():void
		{
			super.configUI();
		}
		
		override protected function onDispose():void
		{
			if (customBG != null) {
				removeChild(customBG);
				customBG = null;
			}
			if (textField != null)
			{
				removeChild(textField);
				textField = null;
			}
			super.onDispose();
		}

		override public function refresh():void
		{
			super.refresh();
		}

		private function updateText():void
		{
			if (text == null || textField == null) {
				return;
			}
			if (isHtml) {
				textField.htmlText = text;
			}
			else {
				textField.text = text;			
			}
			if (customBG != null) {
				updateCustomBackground();
			}
			initialize();
		}

		override protected function updateBorder():void
		{
			if (customBG != null) {
				borderEx.update(textField.x - bg_margin - bg_thickness, textField.y - bg_margin - bg_thickness, textField.width + (bg_margin*2) + (bg_thickness*2), textField.height + (bg_margin*2) + (bg_thickness*2));
			} else {
				borderEx.update(textField.x, textField.y, textField.width, textField.height);
			}
		}
		
		override protected function updateSize():void
		{
			if (autoSize)
			{
				textField.autoSize = TextFieldAutoSize.LEFT;
				// textField.width = _originalWidth;
				// textField.height = _originalHeight;

				// special case for textfield! - we need to update the super class 'width' without setting autosize to none!
				super.setLabelSizes(textField.width, textField.height);
				//FlashUI.ui.py_log("LabelEx:updateSize autoSize:true " + " w:" + textField.width + " h:" + textField.height + " text:"+ textField.htmlText);
			}
			else
			{
				textField.autoSize = TextFieldAutoSize.NONE;
				textField.width = width;
				textField.height = height;
				//FlashUI.ui.py_log("LabelEx:updateSize autoSize:false " + " w:" + textField.width + " h:" + textField.height + " text:"+ textField.htmlText);
			}
			super.updateSize();
		}

		public function get text():String
		{
			return _text;
		}
		
		public function set text(value:String):void
		{
			if (value != _text) _text = value || "";
			updateText();
		}
		
		public function get isHtml():Boolean
		{
			return _isHtml;
		}
		
		public function set isHtml(value:Boolean):void
		{
			if (value != _isHtml) _isHtml = value;
			updateText();
		}
		
		public function get hAlign():String
		{
			return _hAlign;
		}
		
		public function set hAlign(value:String):void
		{
			if (value != _hAlign) _hAlign = value;
		}
		
		public function get vAlign():String
		{
			return _vAlign;
		}
		
		public function set vAlign(value:String):void
		{
			if (value != _vAlign) _vAlign = value;
		}
		
		public function get multiline():Boolean
		{
			return textField.multiline;
		}
		
		public function set multiline(value:Boolean):void
		{
			if (value != textField.multiline) textField.multiline = value;
		}
		
		public function get selectable():Boolean
		{
			return textField.selectable;
		}
		
		public function set selectable(value:Boolean):void
		{
			if (value != textField.selectable) textField.selectable = value;
		}
		
		public function set wordWrap(value:Boolean):void
		{
			if (value != textField.wordWrap) textField.wordWrap = value;
		}
		
		public function get wordWrap():Boolean
		{
			return textField.wordWrap;
		}
		
		public function set background(value:Boolean):void
		{
			if (value != textField.background) textField.background = value;
		}
		
		public function get background():Boolean
		{
			return textField.background;
		}
		
		public function set backgroundColor(value:uint):void
		{
			if (value != textField.backgroundColor) textField.backgroundColor = value;
		}
		
		public function get backgroundColor():uint
		{
			return textField.backgroundColor;
		}
		
		public function set shadow(args:Object):void
		{
			Properties.setShadow(textField, args);
		}

		public function set glowfilter(args:Object):void
		{
			Properties.setGlowFilter(textField, args);
		}

		protected function updateCustomBackground():void
		{
			if (customBG == null)
				return;
			customBG.x = textField.x;
			customBG.y = textField.y;
			customBG.graphics.clear();

			// 1. select if just the border or a filled rect
			customBG.graphics.beginFill(bg_color, bg_fill ? 1.0 : 0);

			//customBG.graphics.lineStyle(bg_thickness, bg_borderColor, 1.0, bg_pixelHinting, bg_scaleMode, bg_caps, bg_joints, bg_miterLimit);
			customBG.graphics.lineStyle(bg_thickness, bg_border ? bg_borderColor : bg_color, 1.0);
			//customBG.graphics.drawRect(0 - bg_margin -  bg_thickness, 0 - bg_margin - bg_thickness, textField.width + (bg_margin * 2) + (bg_thickness * 2), textField.height + (bg_margin * 2) + (bg_thickness * 2));
			if (bg_ellipseWidth > 0) {
				//customBG.graphics.moveTo(0,0)
				customBG.graphics.drawRoundRect(0 - bg_margin - bg_thickness, 0 - bg_margin - bg_thickness, textField.width + (bg_margin*2) + (bg_thickness*2), textField.height + (bg_margin*2) + (bg_thickness*2), bg_ellipseWidth);
			} else {
				customBG.graphics.drawRect     (0 - bg_margin - bg_thickness, 0 - bg_margin - bg_thickness, textField.width + (bg_margin*2) + (bg_thickness*2), textField.height + (bg_margin*2) + (bg_thickness*2));
			}

			if (bg_fill)
				customBG.graphics.endFill();

			customBG.alpha = bg_alpha;
			
		}
		
		public function set customBackground(args:Object):void
		{
			if (!args && customBG != null)
			{
				removeChild(customBG);
				customBG = null;
				return;
			}
			bg_alpha = args.hasOwnProperty('alpha') ? args.alpha : 1.0;
			bg_color = args.hasOwnProperty('color') ? args.color : 0x000000;
			bg_border = args.hasOwnProperty('border') ? args.border : true;
			bg_borderColor = args.hasOwnProperty('borderColor') ? args.borderColor : 0x000000;
			bg_thickness = args.hasOwnProperty('thickness') ? args.thickness : NaN;
			bg_pixelHinting = args.hasOwnProperty('pixelHinting') ? args.pixelHinting : false;
			bg_scaleMode = args.hasOwnProperty('scaleMode') ? args.scaleMode : LineScaleMode.NORMAL;
			bg_caps = args.hasOwnProperty('caps') ? args.caps : CapsStyle.ROUND;
			bg_joints = args.hasOwnProperty('joints') ? args.joints : JointStyle.ROUND;
			bg_miterLimit = args.hasOwnProperty('miterLimit') ? args.miterLimit : 3
			bg_margin = args.hasOwnProperty('margin') ? args.margin : 0
			bg_ellipseWidth = args.hasOwnProperty('ellipseWidth') ? args.ellipseWidth : 0
			bg_fill = args.hasOwnProperty('fill') ? args.fill : true;

			if (customBG == null)
			{
				customBG = new Sprite();
				addChildAt(customBG, 0);
			}
			updateCustomBackground();
		}
	}
}
