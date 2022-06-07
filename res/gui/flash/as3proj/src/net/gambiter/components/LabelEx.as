package net.gambiter.components
{
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.AntiAliasType;
	import flash.text.TextFieldAutoSize;
	
	import net.gambiter.FlashUI;
	import net.gambiter.utils.Align;
	import net.gambiter.utils.Properties;
	import net.gambiter.core.UIComponentEx;
	
	public class LabelEx extends UIComponentEx
	{
		public static const NAME_FONT:String = "$FieldFont";
		
		private var textField:TextField;
		
		private var _text:String;
		private var _isHtml:Boolean;
		private var _hAlign:String;
		private var _vAlign:String;
		
		public function LabelEx()
		{
			super();
			
			textField = new TextField();
			textField.name = "label";
			addChild(textField);
			
			_isHtml = true;			
			_hAlign = Align.LEFT;
			_vAlign = Align.TOP;
			_autoSize = TextFieldAutoSize.LEFT;
			
			textField.width = 0;
			textField.height = 0;
			
			textField.mouseEnabled = false;
			
			textField.wordWrap = false;
			textField.multiline = false;
			textField.selectable = false;
			textField.background = false;
			textField.backgroundColor = 0x000000;
			
			textField.embedFonts = true;
			textField.autoSize = autoSize;
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
		}
		
		override protected function configUI():void
		{
			super.configUI();
		}
		
		override protected function onDispose():void
		{
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
			initialize();
		}

		override protected function updateBorder():void
		{
			borderEx.update(textField.x, textField.y, textField.width, textField.height);
		}
		
		override protected function updateSize():void
		{
			if (autoSize != TextFieldAutoSize.NONE)
			{
				textField.autoSize = autoSize;
				// textField.width = _originalWidth;
				// textField.height = _originalHeight;
			}
			else
			{
				textField.autoSize = TextFieldAutoSize.NONE;
				textField.width = width;
				textField.height = height;
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
		
	}
}