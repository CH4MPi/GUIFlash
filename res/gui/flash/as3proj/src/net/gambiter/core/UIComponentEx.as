package net.gambiter.core
{	
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.display.InteractiveObject;
	
	import net.wg.data.constants.DragType;
	import net.wg.infrastructure.interfaces.entity.IDraggable;
	
	import net.gambiter.FlashUI;
	import net.gambiter.utils.Align;
	import net.gambiter.utils.Properties;
	import net.gambiter.core.UIBorderEx;	
	import scaleform.clik.core.UIComponent;
	
	public class UIComponentEx extends UIComponent implements IDraggable
	{
		protected var borderEx:UIBorderEx;
		
		public var _x:Number;
		public var _y:Number;
		private var _autoSize:Boolean;
		private var _alignX:String;
		private var _alignY:String;		
		private var _drag:Boolean;
		private var _limit:Boolean;
		private var _isDragging:Boolean;
		private var _border:Boolean;
		private var _tooltip:String;
		private var _alias:String;
		private var _index:Number;		
		
		private var _visible:Boolean;
		private var _radialMenu:Boolean;
		private var _fullStats:Boolean;		
		private var _fullStatsQuestProgress:Boolean;
		private var _epicMapOverlayVisible:Boolean;
		private var	_epicRespawnOverlayVisible:Boolean;
		
		public function UIComponentEx()
		{
			super();
			
			borderEx = new UIBorderEx();
			addChild(borderEx);
			
			_x = 0;
			_y = 0;
			_drag = false;
			_limit = true;
			_border = false;
			_autoSize = true;
			_isDragging = false;
			_alignX = Align.LEFT;
			_alignY = Align.TOP;
			
			_visible = true;
			_radialMenu = false;
			_fullStats = false;
			_fullStatsQuestProgress = false;
			_epicMapOverlayVisible = false;
			_epicRespawnOverlayVisible = false;
			
			focusable = false;
		}
		
		override protected function configUI():void
		{
			super.configUI();
			App.cursor.registerDragging(this);
			addEventListener(MouseEvent.MOUSE_OVER, onMouseOver, false, 0, true);
			addEventListener(MouseEvent.MOUSE_OUT, onMouseOut, false, 0, true);
		}
		
		override protected function onDispose():void
		{
			App.cursor.unRegisterDragging(this);
			removeEventListener(MouseEvent.MOUSE_OVER, onMouseOver);
			removeEventListener(MouseEvent.MOUSE_OUT, onMouseOut);
			super.onDispose();
		}
		
		override protected function draw():void
		{
			super.draw();
			// refresh();
		}
		
		public function refresh():void
		{
			updateVisible();
			updateIndex();
			updateSize();
			updateBorder();
			updatePosition();
		}
		
		public function updateVisible():void
		{
			super.visible = _visible &&
				(!FlashUI.ui.showRadialMenu || _radialMenu) &&
				(!FlashUI.ui.showFullStats || _fullStats) &&
				(!FlashUI.ui.showFullStatsQuestProgress || _fullStatsQuestProgress) &&
				(!FlashUI.ui.epicMapOverlayVisibility || _epicMapOverlayVisible) &&
				(!FlashUI.ui.epicRespawnOverlayVisibility || _epicRespawnOverlayVisible);
		}
		
		private function updateIndex():void		
		{
			if (!isNaN(_index) && (_index != parent.getChildIndex(this))) parent.setChildIndex(this, Math.min(_index, parent.numChildren - 1));
		}
		
		protected function updateSize():void
		{
			null;
		}
		
		protected function updateBorder():void
		{
			null;
		}

		public function updatePosition():void
		{		
			super.x = Math.round(_x + (parent.width - width) * Align.getFactor(_alignX));
			super.y = Math.round(_y + (parent.height - height) * Align.getFactor(_alignY));
			if (!_limit) return;			
			var point:Object = Properties.getLimiter(this, super.x, super.y);
			super.x = point.x;
			super.y = point.y;
		}
		
		private function updateProps():void
		{
			var last_x:Number = _x;
			var last_y:Number = _y;			
			_x = Math.round(super.x - (parent.width - width) * Align.getFactor(_alignX));
			_y = Math.round(super.y - (parent.height - height) * Align.getFactor(_alignY));
			if ((_x != last_x) || (_y != last_y))
			{
				py_updateProps({"x": _x, "y": _y});
			}
		}
		
		private function py_updateProps(props:Object):void
		{
			FlashUI.ui.py_update(alias, props);
		}
		
		public function hideCursor():void
		{
			App.toolTipMgr.hide();
			borderEx.hide();
			onEndDrag();
		}
		
		private function onMouseOver(event:MouseEvent):void
		{
			if (!FlashUI.ui.showCursor) return;
			if (_tooltip && !_isDragging) App.toolTipMgr.show(_tooltip);
			if (_border) borderEx.show();
		}
		
		private function onMouseOut(event:MouseEvent):void
		{
			if (_tooltip) App.toolTipMgr.hide();
			if (_border) borderEx.hide();
		}
		
		public function getHitArea():InteractiveObject
		{
			return this;
		}
		
		public function getDragType():String
		{
			return DragType.SOFT;
		}
		
		public function onDragging(_x:Number, _y:Number):void
		{
			null;
		}
		
		public function onStartDrag():void
		{
			if (!FlashUI.ui.showCursor) return;
			if (!_drag) return;
			_isDragging = true;
			_limit ? startDrag(false, Properties.getBound(this)) : startDrag();
			App.toolTipMgr.hide();
		}
		
		public function onEndDrag():void
		{
			if (!_isDragging) return;
			_isDragging = false;
			stopDrag();
			updateProps();
		}		
		
		public function get drag():Boolean
		{
			return _drag;
		}
		
		public function set drag(value:Boolean):void
		{
			if (value != _drag) _drag = value;
		}
		
		public function get limit():Boolean
		{
			return _limit;
		}
		
		public function set limit(value:Boolean):void
		{
			if (value != _limit) _limit = value;
		}
		
		public function get tooltip():String
		{
			return _tooltip;
		}
		
		public function set tooltip(value:String):void
		{
			if (value != _tooltip) _tooltip = value;
		}
		
		public function get alias():String
		{
			return _alias;
		}
		
		public function set alias(value:String):void
		{
			if (value != _alias) _alias = value;
		}
		
		public function get border():Boolean
		{
			return _border;
		}
		
		public function set border(value:Boolean):void
		{
			if (value != _border) _border = value;
		}
		
		public function get index():Number
		{
			return _index;
		}
		
		public function set index(value:Number):void
		{
			if (value != _index) _index = value;
		}
		
		public function get alignX():String
		{
			return _alignX;
		}
		
		public function set alignX(value:String):void
		{
			if ((Align.isValidX(value)) && (value != _alignX)) _alignX = value;
		}
		
		public function get alignY():String
		{
			return _alignY;
		}
		
		public function set alignY(value:String):void
		{
			if ((Align.isValidY(value)) && (value != _alignY)) _alignY = value;
		}
		
		public function get autoSize():Boolean
		{
			return _autoSize;
		}
		
		public function set autoSize(value:Boolean):void
		{
			if (value != _autoSize) _autoSize = value;
		}
		
		override public function set width(value:Number):void
		{
			_autoSize = false;
			super.width = value;
		}
		
		override public function set height(value:Number):void
		{
			_autoSize = false;
			super.height = value;
		}
		
		override public function set x(value:Number):void
		{
			_x = value;
		}
		
		override public function set y(value:Number):void
		{
			_y = value;
		}
		
		override public function set visible(value:Boolean):void
		{
			_visible = value;
		}
		
		public function get radialMenu():Boolean
		{
			return _radialMenu;
		}
		
		public function set radialMenu(value:Boolean):void
		{
			if (value != _radialMenu) _radialMenu = value;
		}
		
		public function get fullStats():Boolean
		{
			return _fullStats;
		}
		
		public function set fullStats(value:Boolean):void
		{
			if (value != _fullStats) _fullStats = value;
		}
		
		public function get fullStatsQuestProgress():Boolean
		{
			return _fullStatsQuestProgress;			
		}
		
		public function set fullStatsQuestProgress(value:Boolean):void
		{
			if (value != _fullStatsQuestProgress) _fullStatsQuestProgress = value;			
		}		
		
	}
}