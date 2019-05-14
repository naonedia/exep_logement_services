/*
 *  Licensed to GIScience Research Group, Heidelberg University (GIScience)
 *
 *   http://www.giscience.uni-hd.de
 *   http://www.heigit.org
 *
 *  under one or more contributor license agreements. See the NOTICE file
 *  distributed with this work for additional information regarding copyright
 *  ownership. The GIScience licenses this file to you under the Apache License,
 *  Version 2.0 (the "License"); you may not use this file except in compliance
 *  with the License. You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
package heigit.ors.routing.graphhopper.extensions;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;

import com.graphhopper.PathWrapper;
import com.graphhopper.routing.util.FlagEncoder;
import com.graphhopper.util.CmdArgs;
import com.graphhopper.util.EdgeIteratorState;
import com.graphhopper.util.Instruction;
import com.graphhopper.util.InstructionAnnotation;
import com.graphhopper.util.InstructionList;
import com.graphhopper.util.PointList;
import com.graphhopper.util.Translation;
import com.graphhopper.util.TranslationMap;
import com.vividsolutions.jts.geom.LineString;
import heigit.ors.mapmatching.RouteSegmentInfo;
import heigit.ors.routing.RoutingProfile;

import com.graphhopper.GHRequest;
import com.graphhopper.GHResponse;
import com.graphhopper.GraphHopper;
import com.graphhopper.reader.DataReader;
import com.graphhopper.routing.Path;
import com.graphhopper.routing.util.EdgeFilter;
import com.graphhopper.storage.GraphHopperStorage;
import com.graphhopper.util.shapes.GHPoint;
import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.GeometryFactory;
import heigit.ors.util.CoordTools;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ORSGraphHopper extends GraphHopper {

    private final Logger logger = LoggerFactory.getLogger(this.getClass());

    private GraphProcessContext _procCntx;
    private HashMap<Long, ArrayList<Integer>> osmId2EdgeIds; // one osm id can correspond to multiple edges
    private HashMap<Integer, Long> tmcEdges;

    // A route profile for referencing which is used to extract names of adjacent streets and other objects.
    private RoutingProfile refRouteProfile;

    public ORSGraphHopper(GraphProcessContext procCntx, boolean useTmc, RoutingProfile refProfile) {
        _procCntx = procCntx;
        this.refRouteProfile = refProfile;
        this.forDesktop();

        if (useTmc) {
            tmcEdges = new HashMap<Integer, Long>();
            osmId2EdgeIds = new HashMap<Long, ArrayList<Integer>>();
        }
        _procCntx.init(this);
    }

    public ORSGraphHopper() {
        // used to initialize tests more easily without the need to create GraphProcessContext etc. when they're anyway not used in the tested functions.
    }

    protected DataReader createReader(GraphHopperStorage tmpGraph) {
        return initDataReader(new ORSOSMReader(tmpGraph, _procCntx, tmcEdges, osmId2EdgeIds, refRouteProfile));
    }

    public boolean load(String graphHopperFolder) {
        boolean res = super.load(graphHopperFolder);


        return res;
    }

    protected void flush() {
        super.flush();
    }

    @SuppressWarnings("unchecked")
    public GraphHopper importOrLoad() {
        GraphHopper gh = super.importOrLoad();


        if ((tmcEdges != null) && (osmId2EdgeIds != null)) {
            java.nio.file.Path path = Paths.get(gh.getGraphHopperLocation(), "edges_ors_traffic");

            if ((tmcEdges.size() == 0) || (osmId2EdgeIds.size() == 0)) {
                // try to load TMC edges from file.

                try {
                    File file = path.toFile();

                    if (file.exists()) {
                        FileInputStream fis = new FileInputStream(path.toString());
                        ObjectInputStream ois = new ObjectInputStream(fis);
                        tmcEdges = (HashMap<Integer, Long>) ois.readObject();
                        osmId2EdgeIds = (HashMap<Long, ArrayList<Integer>>) ois.readObject();
                        ois.close();
                        fis.close();
                        System.out.printf("Serialized HashMap data is saved in trafficEdges");
                    }
                } catch (IOException ioe) {
                    ioe.printStackTrace();
                } catch (ClassNotFoundException c) {
                    System.out.println("Class not found");
                    c.printStackTrace();
                }
            } else {
                // save TMC edges if needed.
                try {
                    FileOutputStream fos = new FileOutputStream(path.toString());
                    ObjectOutputStream oos = new ObjectOutputStream(fos);
                    oos.writeObject(tmcEdges);
                    oos.writeObject(osmId2EdgeIds);
                    oos.close();
                    fos.close();
                    System.out.printf("Serialized HashMap data is saved in trafficEdges");
                } catch (IOException ioe) {
                    ioe.printStackTrace();
                }
            }
        }

        return gh;
    }

    public RouteSegmentInfo getRouteSegment(double[] latitudes, double[] longitudes, String vehicle, EdgeFilter edgeFilter) {
        RouteSegmentInfo result = null;

        GHRequest req = new GHRequest();
        for (int i = 0; i < latitudes.length; i++)
            req.addPoint(new GHPoint(latitudes[i], longitudes[i]));

        req.setVehicle(vehicle);
        req.setAlgorithm("dijkstrabi");
        req.setWeighting("fastest");
        // TODO add limit of maximum visited nodes

        if (edgeFilter != null)
            req.setEdgeFilter(edgeFilter);

        GHResponse resp = new GHResponse();

        List<Path> paths = this.calcPaths(req, resp);

        if (!resp.hasErrors()) {

            List<EdgeIteratorState> fullEdges = new ArrayList<EdgeIteratorState>();
            List<String> edgeNames = new ArrayList<String>();
            PointList fullPoints = PointList.EMPTY;
            long time = 0;
            double distance = 0;
            for (int pathIndex = 0; pathIndex < paths.size(); pathIndex++) {
                Path path = paths.get(pathIndex);
                time += path.getTime();

                for (EdgeIteratorState edge : path.calcEdges()) {
                    //	fullEdges.add(edge.getEdge());
                    fullEdges.add(edge);
                    edgeNames.add(edge.getName());
                }

                PointList tmpPoints = path.calcPoints();

                if (fullPoints.isEmpty())
                    fullPoints = new PointList(tmpPoints.size(), tmpPoints.is3D());

                fullPoints.add(tmpPoints);

                distance += path.getDistance();
            }

            if (fullPoints.size() > 1) {
                Coordinate[] coords = new Coordinate[fullPoints.size()];

                for (int i = 0; i < fullPoints.size(); i++) {
                    double x = fullPoints.getLon(i);
                    double y = fullPoints.getLat(i);
                    coords[i] = new Coordinate(x, y);
                }

                //throw new Exception("TODO");
                result = new RouteSegmentInfo(fullEdges, distance, time, new GeometryFactory().createLineString(coords));
            }
        }

        return result;
    }

    private int _minNetworkSize = 200;
    private int _minOneWayNetworkSize = 0;
    @Override
    public GraphHopper init(CmdArgs args) {
        GraphHopper ret = super.init(args);
        _minNetworkSize = args.getInt("prepare.min_network_size", _minNetworkSize);
        _minOneWayNetworkSize = args.getInt("prepare.min_one_way_network_size", _minOneWayNetworkSize);
        return ret;
    }

    @Override
    protected void cleanUp() {
        logger.info("call cleanUp for '" + getGraphHopperLocation() + "' ");
        GraphHopperStorage ghs = getGraphHopperStorage();
        if (ghs != null) {
            this.logger.info("graph " + ghs.toString() + ", details:" + ghs.toDetailsString());
            int prevNodeCount = ghs.getNodes();
            int ex = ghs.getAllEdges().getMaxId();
            List<FlagEncoder> list = getEncodingManager().fetchEdgeEncoders();
            this.logger.info("will create PrepareRoutingSubnetworks with:\r\n"+
                            "\tNodeCountBefore: '" + prevNodeCount+"'\r\n"+
                            "\tgetAllEdges().getMaxId(): '" + ex+"'\r\n"+
                            "\tList<FlagEncoder>: '" + list+"'\r\n"+
                            "\tminNetworkSize: '" + _minNetworkSize+"'\r\n"+
                            "\tminOneWayNetworkSize: '" + _minOneWayNetworkSize+"'"
            );
        } else {
            this.logger.info("graph GraphHopperStorage is null?!");
        }
        super.cleanUp();
    }


    public GHResponse constructFreeHandRoute(GHRequest request) {
        LineString directRouteGeometry = constructFreeHandRouteGeometry(request);
        PathWrapper directRoutePathWrapper = constructFreeHandRoutePathWrapper(directRouteGeometry);
        GHResponse directRouteResponse = new GHResponse();
        directRouteResponse.add(directRoutePathWrapper);
        directRouteResponse.getHints().put("skipped_segment", "true");
        return directRouteResponse;
    }

    private PathWrapper constructFreeHandRoutePathWrapper(LineString lineString) {
        PathWrapper pathWrapper = new PathWrapper();
        PointList pointList = new PointList();
        PointList startPointList = new PointList();
        PointList endPointList = new PointList();
        PointList wayPointList = new PointList();
        Coordinate startCoordinate = lineString.getCoordinateN(0);
        Coordinate endCoordinate = lineString.getCoordinateN(1);
        double distance = CoordTools.calcDistHaversine(startCoordinate.x, startCoordinate.y, endCoordinate.x, endCoordinate.y);
        pointList.add(lineString.getCoordinateN(0).x, lineString.getCoordinateN(0).y);
        pointList.add(lineString.getCoordinateN(1).x, lineString.getCoordinateN(1).y);
        wayPointList.add(lineString.getCoordinateN(0).x, lineString.getCoordinateN(0).y);
        wayPointList.add(lineString.getCoordinateN(1).x, lineString.getCoordinateN(1).y);
        startPointList.add(lineString.getCoordinateN(0).x, lineString.getCoordinateN(0).y);
        endPointList.add(lineString.getCoordinateN(1).x, lineString.getCoordinateN(1).y);
        Translation translation = new TranslationMap.ORSTranslationHashMapWithExtendedInfo(new Locale(""));
        InstructionList instructions = new InstructionList(translation);
        Instruction startInstruction = new Instruction(Instruction.REACHED_VIA, "free hand route", new InstructionAnnotation(0, ""), startPointList);
        Instruction endInstruction = new Instruction(Instruction.FINISH, "end of free hand route", new InstructionAnnotation(0, ""), endPointList);
        instructions.add(0, startInstruction);
        instructions.add(1, endInstruction);
        pathWrapper.setDistance(distance);
        pathWrapper.setAscend(0.0);
        pathWrapper.setDescend(0.0);
        pathWrapper.setTime(0);
        pathWrapper.setInstructions(instructions);
        pathWrapper.setWaypoints(wayPointList);
        pathWrapper.setPoints(pointList);
        pathWrapper.setRouteWeight(0.0);
        pathWrapper.setDescription(new ArrayList<>());
        pathWrapper.setImpossible(false);
        startInstruction.setDistance(distance);
        startInstruction.setTime(0);
        return pathWrapper;
    }

    private LineString constructFreeHandRouteGeometry(GHRequest request){
        Coordinate start = new Coordinate();
        Coordinate end = new Coordinate();
        start.x = request.getPoints().get(0).getLat();
        start.y = request.getPoints().get(0).getLon();
        end.x = request.getPoints().get(1).getLat();
        end.y = request.getPoints().get(1).getLon();
        Coordinate[] coords = new Coordinate[]{start, end};
        return new GeometryFactory().createLineString(coords);
    }

    public HashMap<Integer, Long> getTmcGraphEdges() {
        return tmcEdges;
    }

    public HashMap<Long, ArrayList<Integer>> getOsmId2EdgeIds() {
        return osmId2EdgeIds;
    }
}