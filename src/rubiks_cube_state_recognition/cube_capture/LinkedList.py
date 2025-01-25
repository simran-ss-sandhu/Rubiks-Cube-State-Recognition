class LlNode:  # linked list node
    def __init__(self, possible_cube_tiles: list, possible_cube_faces: list):
        self.index_pointer = None  # pointer to the index of this node in the nodes list
        self.next_pointer = None  # pointer to the nodes list index of the next node in the linked list

        # the squares that have been flagged as possible cube tiles
        # the linked list will be sorted in decreasing order of the length of this attribute
        self.possible_cube_tiles = possible_cube_tiles

        # the squares that have been flagged as being a possible cube face (that has the possible cube tiles within it)
        self.possible_cube_faces = possible_cube_faces


class LinkedList:
    def __init__(self):
        self.start_pointer = -1  # the index of the node in the nodes list that is at the front of the linked list
        self.next_free_pointer = 0  # the index of the next free space in the nodes list
        self.nodes = []  # the nodes in the linked list

    def insert_node(self, node_to_insert: LlNode):
        # node will be inserted at the next free space in the nodes list
        # this updates the index accordingly
        node_to_insert.index_pointer = self.next_free_pointer

        if self.start_pointer == -1:  # if no nodes have been added yet
            self.start_pointer = 0  # the index of the front of the list (the insertion index)

        else:  # the linked list is not empty

            # finds length of node lists
            node_to_insert_tiles_len = len(node_to_insert.possible_cube_tiles)
            node_to_insert_faces_len = len(node_to_insert.possible_cube_faces)

            previous_node = None  # the node that will be before insertion node
            after_node = self.nodes[self.start_pointer]  # the node that will be after the insertion node

            # finds the values of the previous and after nodes (what two nodes to insert between)
            while True:  # while insertion position hasn't been found
                after_node_tiles_len = len(
                    after_node.possible_cube_tiles)  # finds the length of the after node cube tiles list

                # the node is ready to be inserted before the after node (as its cube tiles list length is larger)
                if node_to_insert_tiles_len > after_node_tiles_len:
                    break

                # the node's cube faces list length will decide the insertion position (as the cube tiles lists lengths are the same)
                elif node_to_insert_tiles_len == after_node_tiles_len:
                    after_node_faces_len = len(
                        after_node.possible_cube_faces)  # finds the length of the after node cube faces list

                    # the node is ready to be inserted in front of the after node (as its cube faces list length is larger)
                    if node_to_insert_faces_len >= after_node_faces_len:
                        break

                # updates previous and after node varaibles for search in the next iteration (with the next node in the linked list)
                previous_node = after_node
                if after_node.next_pointer is not None:  # if the after node is not the last node in the linked list
                    after_node = self.nodes[after_node.next_pointer]  # becomes the next node in the linked list
                else:  # the after node is the last node in the linked list (insertion node has the smallest cube tiles list length in the linked list)
                    after_node = None  # there is no node to direct the next pointer to
                    break

            # updates the previous node's next_pointer so that it directs to the insertion node
            if previous_node is not None:  # if the insertion node won't be inserted at the front of the linked list
                index = previous_node.index_pointer
                self.nodes[index].next_pointer = node_to_insert.index_pointer

            # the insertion position is at the front of the list
            # the start pointer has to be updated
            else:
                self.start_pointer = node_to_insert.index_pointer

            # updates the insertion node's next_pointer to direct to the after_node
            if after_node is not None:  # makes sure that the insertion node will not be the last node in the linked list
                node_to_insert.next_pointer = after_node.index_pointer
            # else:
            #   the insertion node will be the last node in the linked list
            #   the next_pointer will not point to anything (does not need updating)

        # inserts the insertion node with updated pointers to the nodes list
        self.nodes.insert(node_to_insert.index_pointer,  # list index to insert at
                          node_to_insert)  # item to insert

        # updates the value of the next free space pointer
        self.next_free_pointer += 1

