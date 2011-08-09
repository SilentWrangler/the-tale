if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.map) {
    pgf.game.map = {};
}

if (!pgf.game.resources) {
    pgf.game.resources = {};
}

pgf.game.resources.Image = function(canvas) {
    var image = canvas;

    this.Draw = function(context, x, y) {
        context.drawImage(image, x, y);
    }
};

pgf.game.resources.ImageManager =  function(spritesSettins, params) {

    var spritesSources = {};

    var loadedSources = 0;
    var totalSources = 0;

    var initializedSprites = 0;
    var totalSprites = 0;

    var sprites = {};

    function InitializeSourceSprites(properties) {
        for( spriteName in spritesSettins) {
            if (spritesSettins[spriteName].src == properties.src) {

                var data = spritesSettins[spriteName];

                var tmpCanvas = document.createElement('canvas');
                tmpCanvas.width = data.w;
                tmpCanvas.height = data.h;
                var tmpContext = tmpCanvas.getContext('2d');

                tmpContext.drawImage(properties.image, 
                                     data.x, data.y, data.w, data.h,
                                     0, 0, data.w, data.h);

                sprites[spriteName] = new pgf.game.resources.Image(tmpCanvas);
                initializedSprites += 1;
            }
        }

        if (initializedSprites == totalSprites) {
            if (params.OnSpritesInitialized) {
                params.OnSpritesInitialized();
            }
        }
    }

    for(spriteName in spritesSettins) {
        var data = spritesSettins[spriteName];

        totalSprites += 1;

        if (spritesSources[data.src] == undefined) {
            spritesSources[data.src] = true;
            totalSources += 1;

            (function() {
                var image = new Image();
                var sourceProperties = { loaded: false,
                                         image: image,
                                         src: data.src,
                                         error: undefined };

                image.onload = function(e) {
                    sourceProperties.loaded = true;
                    loadedSources += 1;
                    InitializeSourceSprites(sourceProperties);
                };
                image.src = params.staticUrl + data.src;
            })();
        }
    }

    this.GetImage = function(name) {
        return sprites[name];
    }

    this.IsReady = function(){ return (initializedSprites == totalSprites); };
};

pgf.game.map.MapManager = function(params) {

    var mapData = {};
    var calculatedData = {};
    var dynamicData = { heroes: {} };
    var updater = params.updater;
    var instance = this;

    jQuery.ajax({
        dataType: 'json',
        type: 'get',
        url: params.regionUrl,
        success: function(data, request, status) {
            mapData = data;

            calculatedData.roadsMap = CalculateRoads(mapData);

            instance.mapWidth = data.width;
            instance.mapHeight = data.height;
            
            if (params.OnDataUpdated) {
                params.OnDataUpdated();
            }
        },
        error: function() {
        },
        complete: function() {
        }
    });

    function CalculateRoads(mapData) {
        var w = mapData.width;
        var h = mapData.height;
        
        var roadsMap = [];
        for (var i=0; i<h; ++i) {
            var row = []
            for (var j=0; j<w; ++j) {
                row.push('.');
            }
            roadsMap.push(row);
        }

        for(var road_id in mapData.roads) {
            var road = mapData.roads[road_id];
            var point_1 = mapData.places[road.point_1_id];
            var x = point_1.x;
            var y = point_1.y;

            roadsMap[y][x] = 'r';
            for(var i=0; i<road.path.length; ++i) {
                switch(road.path[i]) {
                case 'l': x -= 1; break;
                case 'r': x += 1; break;
                case 'u': y -= 1; break;
                case 'd': y += 1; break;
                }
                
                roadsMap[y][x] = 'r';
            }
        }

        return roadsMap;
    }
    
    function RefreshHero(hero) {
        dynamicData.heroes[hero.id] = hero;
    }
    
    function GetMapDataForRect(x, y, w, h) {
        return { mapData: mapData, 
                 dynamicData: dynamicData,
                 calculatedData: calculatedData};
    }

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){

        for (var hero_id in updater.data.data.heroes) {
            RefreshHero(updater.data.data.heroes[hero_id]);
        }

        if (params.OnDataUpdated) {
            params.OnDataUpdated();
        }

    });

    this.mapWidth = 0;
    this.mapHeight = 0;

    this.GetMapDataForRect = GetMapDataForRect;
}; 

pgf.game.map.Map = function(selector, params) {

    var map = jQuery(selector);
    var canvas = jQuery('.pgf-map-canvas', selector);

    var canvasWidth = canvas.width();
    var canvasHeight = canvas.height();

    map.css({width: canvasWidth,
             height: canvasHeight });

    var mapUrl = params.mapUrl;

    var spritesManager = params.spritesManager;
    var mapManager = new pgf.game.map.MapManager({regionUrl:  mapUrl + 'region.js',
                                                  updater: updater,
                                                  OnDataUpdated: function() {
                                                      Refresh();
                                                  }
                                                 });

    var pos = {x: 0, y: 0};

    var TILE_SIZE = params.tileSize;

    var subsytemsReady = false;

    var navigationLayer = new pgf.game.map.NavigationLayer(jQuery('.pgf-navigation-layer'), 
                                                           { OnMove: OnMove,
                                                             w: canvasWidth,
                                                             h: canvasHeight
                                                           });

    function OnMove(dx, dy) {

        if (!subsytemsReady) return;

        pos.x -= dx;
        pos.y -= dy;

        if (pos.x > 0) pos.x = 0;
        if (pos.y > 0) pos.y = 0;
        if (mapManager.mapWidth * TILE_SIZE + pos.x < canvasWidth) pos.x = canvasWidth - mapManager.mapWidth * TILE_SIZE;
        if (mapManager.mapHeight * TILE_SIZE + pos.y < canvasHeight) pos.y = canvasHeight - mapManager.mapHeight * TILE_SIZE;

        var data = mapManager.GetMapDataForRect(pos.x, pos.y, canvasWidth, canvasHeight);
        Draw(data);
    }

    function GetRoadTile(map, y, x) {
        var result = {name: '',
                      rotate: 0};
        var l = 1 ? (x > 0 && map[y][x-1] != '.') : 0;
        var r = 1 ? ((x < map[y].length-1) && map[y][x+1] != '.') : 0;
        var u = 1 ? (y > 0 && map[y-1][x] != '.') : 0;
        var d = 1 ? ((y < map.length-1) && map[y+1][x] != '.') : 0;

        var sum = l + r + u + d;

        if (sum==4)return {name: 'r4', rotate: 0};
        
        if (sum==3) {
            if (!l) return {name: 'r3', rotate: 90};
            if (!r) return {name: 'r3', rotate: 270};
            if (!u) return {name: 'r3', rotate: 180};
            if (!d) return {name: 'r3', rotate: 0};
        }

        if (l && u) return {name: 'r_angle', rotate: 0};
        if (l && r) return {name: 'r_line', rotate: 0};
        if (l && d) return {name: 'r_angle', rotate: 270};

        if (u && r) return {name: 'r_angle', rotate: 90};
        if (u && d) return {name: 'r_line', rotate: 90};

        if (r && d) return {name: 'r_angle', rotate: 180};

        if (l || r) return {name: 'r_line', rotate: 0};
        if (u || d) return {name: 'r_line', rotate: 90};

        alert('check cell: ('+x+', '+y+')');
        return {name: 'r_line', rotate: 0};
    }

    function Draw(fullData) {
        
        if (!subsytemsReady) return;

        data = fullData.mapData;
        dynamicData = fullData.dynamicData;
        calculatedData = fullData.calculatedData;

        var context = canvas.get(0).getContext("2d");
        
        context.save();

        var w = data.width;
        var h = data.height;
        var terrain = data.terrain;

        for (var i=0; i<h; ++i) {               
            for (var j=0; j<w; ++j) {
                var image = undefined;
                var rotate = 0;

                var x = pos.x + j * TILE_SIZE;
                var y = pos.y + i * TILE_SIZE;

                if (calculatedData.roadsMap[i][j] != '.') {
                    var roadTile = GetRoadTile(calculatedData.roadsMap, i, j);
                    image = spritesManager.GetImage(roadTile.name);
                    rotate = roadTile.rotate * Math.PI / 180;

                    context.save();
                    var translated_x = x + TILE_SIZE / 2;
                    var translated_y = y + TILE_SIZE / 2;
                    context.translate(translated_x, translated_y);
                    context.rotate(rotate);
                    image.Draw(context, -TILE_SIZE/2, -TILE_SIZE/2);
                    context.restore();

                }
                else {
                    image = spritesManager.GetImage(terrain[i][j]);
                    image.Draw(context, x, y);
                }
            }
        }
        
        for (var place_id in data.places) {
            var place = data.places[place_id];
            var image = spritesManager.GetImage('place');
            image.Draw(context, 
                       pos.x + place.x * TILE_SIZE, 
                       pos.y + place.y * TILE_SIZE);
        }

        for (var hero_id in dynamicData.heroes) {
            var hero = dynamicData.heroes[hero_id];
            var image = spritesManager.GetImage('hero');

            var x = 0;
            var y = 0;

            if (hero.position.place) {
                var place = data.places[hero.position.place.id];
                x = place.x * TILE_SIZE;
                y = place.y * TILE_SIZE;
                image.Draw(context, pos.x + x, pos.y + y);
            }
            if (hero.position.road) {
                var road = data.roads[hero.position.road.id];
                var point_1 = data.places[road.point_1_id];
                var point_2 = data.places[road.point_2_id];

                var percents = hero.position.percents;
                var path = road.path;
                var x = point_1.x;
                var y = point_1.y;
                if (hero.position.invert_direction) {
                    percents = 1 - percents;
                }
                var length = percents * path.length;
                for (var i=0; i+1<length; ++i) {
                    switch(path[i]) {
                    case 'l': x -= 1; break;
                    case 'r': x += 1; break;
                    case 'u': y -= 1; break;
                    case 'd': y += 1; break;
                    }
                }
                
                var delta = length - i;
                switch(path[i]) {
                    case 'l': x -= delta; break;
                    case 'r': x += delta; break;
                    case 'u': y -= delta; break;
                    case 'd': y += delta; break;
                }

                image.Draw(context, 
                           pos.x + x * TILE_SIZE , 
                           pos.y + y * TILE_SIZE);
            }
        }

        context.restore();
    }

    function Activate() {
        OnMove(0, 0);
    }

    function Refresh() {
        OnMove(0, 0);
    }

    function CheckReadyState() {
        if (spritesManager.IsReady()) {
            subsytemsReady = true;
        }
        Activate();
    }

    this.Draw = Draw;
    this.CheckReadyState = CheckReadyState;

};


pgf.game.map.NavigationLayer = function(selector, params) {

    var container = jQuery(selector);
    container.css({width: params.w,
                   height: params.h });

    var pos = {x: 0, y: 0};

    var OnMove = params.OnMove;

    var layer = this;

    function OnStartDragging(e, ui) {
        pos = {x: ui.position.left,
               y: ui.position.top};
    };

    function OnDrag(e, ui) {
        var newPos = {x: ui.position.left,
                      y: ui.position.top};

        var delta = {x: pos.x - newPos.x,
                     y: pos.y - newPos.y};

        pos = newPos;

        OnMove(delta.x, delta.y);
    };

    function OnStopDragging(e, ui) {
    };

    container.draggable({start: function(e, ui){OnStartDragging(e, ui);},
                         drag: function(e, ui){OnDrag(e, ui);},
                         stop: function(e, ui){OnStopDragging(e, ui);},
                         cursor: 'crosshair',
                         helper: 'original',
                         revert: true,
                         revertDuration: 0,
                         scroll: false,
                        });
};

