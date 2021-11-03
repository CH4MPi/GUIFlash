package net.gambiter.core
{
	import flash.geom.Rectangle;
	import flash.display.Shape;
	import flash.display.DisplayObject;
	
	public class UIBorderEx extends Shape
	{
		private var _rect:Rectangle;
		private var _obj:DisplayObject;
		
		public function UIBorderEx()
		{
			super();
			
			visible = false;
			_rect = new Rectangle(0, 0, 0, 0);
		}
		
		private function draw():void
		{
			graphics.clear();
			graphics.beginFill(0x999999, 0.1);
			graphics.lineStyle(1, 0x999999, 1, true);
			graphics.drawRect(_rect.x, _rect.y, _rect.width, _rect.height);
			graphics.endFill();
		}
		
		public function show():void
		{
			if (_obj) _rect = _obj.getRect(_obj);
			draw();
			visible = true;
		}
		
		public function hide():void
		{
			graphics.clear();
			visible = false;
		}
		
		public function update(_x_:Number, _y_:Number, _w_:Number, _h_:Number):void
		{
			_rect = new Rectangle(_x_, _y_, _w_, _h_);
		}
		
		public function get obj():DisplayObject
		{
			return _obj;
		}
		
		public function set obj(value:DisplayObject):void
		{
			if (value != _obj) _obj = value;
		}
	}
}
