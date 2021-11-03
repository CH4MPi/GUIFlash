package net.gambiter.utils
{
	import flash.display.DisplayObject;
	
	import net.gambiter.components.PanelEx;
	import net.gambiter.components.LabelEx;
	import net.gambiter.components.ImageEx;
	// import net.gambiter.components.ShapeEx;
	
	public class Components
	{
		public static const COMPONENT_TYPE_PANEL:String = "Panel";
		public static const COMPONENT_TYPE_LABEL:String = "Label";
		public static const COMPONENT_TYPE_IMAGE:String = "Image";
		public static const COMPONENT_TYPE_SHAPE:String = "Shape";
		
		public static function getClass(value:String):DisplayObject
		{
			switch (value)
			{
				case COMPONENT_TYPE_PANEL:
					return new PanelEx();
				case COMPONENT_TYPE_LABEL:
					return new LabelEx();
				case COMPONENT_TYPE_IMAGE:
					return new ImageEx();
				// case COMPONENT_TYPE_SHAPE:
				//	return new ShapeEx();
				default:
					return null;
			}
		}
	}
}