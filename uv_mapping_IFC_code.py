    def create_triangulated_face_set(self):
        ifc_raw_items = [None] * self.settings["total_items"]
        if self.settings["should_generate_uvs"]:
            ifc_raw_uv_items = [None] * self.settings["total_items"]
        for i, value in enumerate(ifc_raw_items):
            ifc_raw_items[i] = []
            if self.settings["should_generate_uvs"]:
                ifc_raw_uv_items[i] = []
        for polygon in self.settings["geometry"].polygons:
            ifc_raw_items[polygon.material_index % self.settings["total_items"]].append(
                [v + 1 for v in polygon.vertices]
            )
            if self.settings["should_generate_uvs"]:
                ifc_raw_uv_items[polygon.material_index % self.settings["total_items"]].append(
                    [uv + 1 for uv in polygon.loop_indices]
                )

        coordinates = self.file.createIfcCartesianPointList3D(
            [self.convert_si_to_unit(v.co) for v in self.settings["geometry"].vertices]
        )

        if self.settings["should_generate_uvs"]:
            # Blender supports multiple UV layers. We don't. Too bad.
            tex_coords = self.file.createIfcTextureVertexList(
                [tuple(x.uv) for x in self.settings["geometry"].uv_layers[0].data]
            )
            items = []
            for i, coord_index in enumerate(ifc_raw_items):
                if not coord_index:
                    continue
#-----------------------------------------------------------------------------------------------------------------------------            
                #This assigns every triangle their own Cartesian Points.
                tempCoord_IndexList=[]
                finalCoord_IndexList=[]
                for x in (coord_index):
                    tempCoord_IndexList = x
                    for v in range(len(tempCoord_IndexList)):
                        if len(tempCoord_IndexList) >= v:
                            finalCoord_IndexList.append(coordinates.CoordList[tempCoord_IndexList[v]-1])
                coordinates.CoordList = finalCoord_IndexList
                #This assigns the new order of Tuples to IfcTriangulatedFaceSet
                coord_index = ifc_raw_uv_items[0]
#------------------------------------------------------------------------------------------------------------------------------

                tex_coords_index = ifc_raw_uv_items[i]
                face_set = self.file.createIfcTriangulatedFaceSet(coordinates, None, None, coord_index)
                texture_map = self.file.createIfcIndexedTriangleTextureMap(
                    MappedTo=face_set, TexCoords=tex_coords, TexCoordIndex=tex_coords_index
                )
                items.append(face_set)
        else:
            items = [self.file.createIfcTriangulatedFaceSet(coordinates, None, None, i) for i in ifc_raw_items if i]

        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Tessellation",
            items,
        )
