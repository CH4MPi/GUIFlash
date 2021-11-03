package net.gambiter.utils
{
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.filters.DropShadowFilter;
	import flash.filters.GlowFilter;
	
	import com.greensock.TweenLite;
	
	import net.gambiter.FlashUI;
	import net.gambiter.core.UIComponentEx;
	import net.gambiter.components.ImageEx;

	public class Properties
	{
		public static function getBound(obj:DisplayObject):Rectangle
		{
			var objRect:Rectangle = obj.getRect(obj);
			var objPoint:Point = obj.localToGlobal(new Point(0, 0));

			return new Rectangle(
				obj.x - objPoint.x - objRect.x,
				obj.y - objPoint.y - objRect.y,
				FlashUI.ui.screenSize.width - objRect.width,
				FlashUI.ui.screenSize.height - objRect.height
			);
		}

		public static function getLimiter(obj:DisplayObject, obj_x:Number, obj_y:Number):Object
		{
			var point:Object = {x: obj_x, y: obj_y};
			var rect:Rectangle = getBound(obj);

			point.x = Math.max(point.x, rect.x);
			point.y = Math.max(point.y, rect.y);
			point.x = Math.min(point.x, rect.width);
			point.y = Math.min(point.y, rect.height);

			return point;
		}

		public static function setShadow(obj:DisplayObject, props:Object = null):void
		{
			if (!obj) return;
		
			if (props)
			{
				var shadow:DropShadowFilter = new DropShadowFilter();
				for (var prop:String in props) {
					if (shadow.hasOwnProperty(prop)) {
						shadow[prop] = props[prop];
					}
				}
				obj.filters = [shadow];
			}
			else obj.filters = null;
		}

		public static function setGlowFilter(obj:DisplayObject, props:Object = null):void
		{
			if (!obj) return;
			if (props)
			{
				var filter:GlowFilter = new GlowFilter();
				for (var prop:String in props) {
					if (filter.hasOwnProperty(prop)) {
						filter[prop] = props[prop];
					}
				}
				obj.filters = [filter];
			}
			else obj.filters = null;
		}

		public static function setProperty(obj:DisplayObject, props:Object):void
		{
			if (!obj || !props) return;
			
			for (var prop:String in props)
			{
				// TEST: glowfilter as property
				//if (prop == 'glowfilter') {
					//FlashUI.ui.py_log("property glowgilter found!");
					//Properties.setGlowFilter(obj, props);
					////props.pop(prop);
					//continue;
				//}
//
				if (obj.hasOwnProperty(prop)) {
					obj[prop] = props[prop];
					continue;
				}
				FlashUI.ui.py_log("Object with linkage \'" + obj.name + "\' doesn`t contain property " + "with name \'" + prop + "\'.");
			}

			if (obj is UIComponentEx) {
				(obj as UIComponentEx).refresh();
			}
		}

		public static function setAnimateProperty(obj:DisplayObject, props:Object, params:Object):void
		{
			if (!obj || !props) return;

			var tweens:Object = new Object();

			var from:Boolean = params.hasOwnProperty('from') && params.from;
			var start:Boolean = params.hasOwnProperty('start') && params.start;
			var delay:Number = params.hasOwnProperty('delay') ? params.delay : 0;
			var duration:Number = params.hasOwnProperty('duration') ? params.duration : 0;

			if (!duration) { setProperty(obj, props); return; }

			for (var prop:String in props)
			{
				if (prop != "x" && prop != "y" && prop != "alpha" && prop != "rotation" && prop != "scaleX" && prop != "scaleY") continue;
				tweens[((prop == "x") || (prop == "y")) ? ("_" + prop) : prop] = props[prop];
				delete props[prop];
			}

			if (delay) tweens.delay = params.delay;
			
			if (obj is UIComponentEx) tweens.onUpdate = (obj as UIComponentEx).refresh;
			
			if (start) { tweens.onStart = setProperty; tweens.onStartParams = [obj, props]; }
			else { tweens.onComplete = setProperty; tweens.onCompleteParams = [obj, props]; }

			if (from) TweenLite.from(obj, duration, tweens);
			else TweenLite.to(obj, duration, tweens);
		}

		private static function isEmptyObject(obj:Object):Boolean
		{
			var isEmpty:Boolean = true;
			for (var prop:String in obj) { isEmpty = false; break; }
			return isEmpty;
		}

		public static function getComponentByPath(container:DisplayObjectContainer, path:Array):DisplayObject
		{
			var component:DisplayObject = container as DisplayObject;

			for each (var item:String in path)
			{
				if (!container) break;
				component = container.getChildByName(item);
				if (!component) break;
				container = component as DisplayObjectContainer;
			}
			return component;
		}

		public static function traceDisplayList(container:DisplayObjectContainer, indent:String = ""):void
		{
			for (var i:uint = 0; i < container.numChildren; i++)
			{
				var component:DisplayObject = container.getChildAt(i);
				FlashUI.ui.py_log(indent, i, component.name);
				if (container.getChildAt(i) is DisplayObjectContainer) traceDisplayList(component as DisplayObjectContainer, indent + " --| ")
			}
		}
	}
}