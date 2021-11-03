package net.gambiter.components
{
	import flash.display.Loader;
	import flash.events.Event;
	import flash.events.IOErrorEvent;
	import flash.net.URLRequest;
	
	import net.gambiter.utils.Properties;
	import net.gambiter.core.UIComponentEx;
	
	public class ImageEx extends UIComponentEx
	{
		private var loader:Loader;
		
		private var _source:String;
		private var _sourceAlt:String;
		private var _loadFailed:Boolean;
		private var _loadInProgress:Boolean;
		private var _previousContentUnloaded:Boolean;
		
		public function ImageEx()
		{
			super();
			
			loader = new Loader();
			loader.name = "image";
			addChild(loader);
			
			_source = "";
			_sourceAlt = "";
			_loadFailed = false;
			_loadInProgress = false;
			_previousContentUnloaded = true;
			
			addLoaderListener();
		}
		
		override protected function configUI():void
		{
			super.configUI();
		}
		
		override protected function onDispose():void
		{
			if (loader != null)
			{
				removeLoaderListener();
				unload();
				removeChild(loader);
				loader = null;
			}
			super.onDispose();
		}
		
		override protected function updateBorder():void
		{
			borderEx.update(loader.x, loader.y, loader.width, loader.height);
		}
		
		override protected function updateSize():void
		{
			if (_loadFailed || _loadInProgress) return;
			if (autoSize)
			{
				loader.width = _originalWidth;
				loader.height = _originalHeight;
			}
			else
			{
				loader.width = width;
				loader.height = height;
			}
			super.updateSize();
		}
		
		private function startLoad(url:String):void
		{
			_source = url;
			if (!_previousContentUnloaded) loader.unload();
			loader.visible = false;
			_loadInProgress = true;
			_previousContentUnloaded = false;
			loader.load(new URLRequest(url));
		}
		
		private function startLoadAlt():void
		{
			startLoad(_sourceAlt);
		}
		
		private function loadComplete():void
		{
			loader.visible = true;
		}
		
		private function unload():void
		{
			if (_loadInProgress) loader.close();
			loader.unload();
			_source = null;
		}
		
		private function addLoaderListener():void
		{
			loader.contentLoaderInfo.addEventListener(Event.COMPLETE, onLoaderCompleteHandler);
			loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR, onLoaderIoErrorHandler);
			loader.contentLoaderInfo.addEventListener(Event.UNLOAD, onLoaderUnloadHandler);
		}
		
		private function removeLoaderListener():void
		{
			loader.contentLoaderInfo.removeEventListener(Event.COMPLETE, onLoaderCompleteHandler);
			loader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR, onLoaderIoErrorHandler);
			loader.contentLoaderInfo.removeEventListener(Event.UNLOAD, onLoaderUnloadHandler);
		}
		
		private function onLoaderCompleteHandler(e:Event):void
		{
			_loadFailed = false;
			_loadInProgress = false;
			initialize();
			refresh();
			loadComplete();
		}
		
		private function onLoaderIoErrorHandler(e:IOErrorEvent):void
		{
			if (!_loadFailed && _sourceAlt)
			{
				_loadFailed = true;
				startLoad(_sourceAlt);
			}
			else _loadInProgress = false;
		}
		
		private function onLoaderUnloadHandler(e:Event):void
		{
			_previousContentUnloaded = true;
		}
		
		public function get image():String
		{
			return _source;
		}
		
		public function set image(url:String):void
		{
			_loadFailed = false;
			if (!url || url == _source) return;
			startLoad(url);
		}
		
		public function get imageAlt():String
		{
			return _sourceAlt;
		}
		
		public function set imageAlt(url:String):void
		{
			if (!url || _sourceAlt == url) return;
			_sourceAlt = url;
			if (_loadFailed) startLoad(url);
		}
	}
}