import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import MenuList from '@mui/material/MenuList';
import MenuItem from '@mui/material/MenuItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import {Add, Close, Delete, Edit, CheckBox} from "@mui/icons-material"
import {NodeContextType, NodeType, PDDLGraphNode} from "./NodeContext.tsx";
import {NodeModalContextType} from "./NodeModal.tsx";
import {useEffect} from "react";

export type NodeMenuProps = {
    node: PDDLGraphNode;
    onClose: () => void,
    nodeContext: NodeContextType,
    nodeModalContext: NodeModalContextType,
    graphContainerRef: any
};

export const NodeMenu = (props: NodeMenuProps) => {

    const {nodeContext, onClose, node, nodeModalContext, graphContainerRef} = props;

    useEffect(() => {
        if(!graphContainerRef.current)
            return
        const canvas = graphContainerRef.current.getElementsByTagName("canvas")[0];
        canvas.onclick = () => onClose()
    }, [graphContainerRef])

    return <Paper sx={{width: 320, maxWidth: '100%', position: 'relative', left: 160, top: 168 / 2}}>
        <MenuList>
            <MenuItem onClick={props.onClose}>
                <ListItemIcon>
                    <Close fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Close Menu</ListItemText>
            </MenuItem>
            <Divider/>

            <MenuItem onClick={() => {
                nodeContext.add_new(node.id, {
                    type: NodeType.WAYPOINT,
                    label: "New State",
                    predicates: []
                })
                onClose()
            }}>
                <ListItemIcon>
                    <Add fontSize="small"/>
                </ListItemIcon>
                <ListItemText>New Waypoint</ListItemText>
            </MenuItem>

            {node.type !== NodeType.START && <MenuItem onClick={() => {
                nodeContext.remove(node.id)
                onClose()
            }}>
                <ListItemIcon>
                    <Delete fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Delete Node</ListItemText>
            </MenuItem>}

            {node.type !== NodeType.START && <MenuItem onClick={() => {
                nodeModalContext.show(node.id)
                onClose()
            }}>
                <ListItemIcon>
                    <Edit fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Edit Node</ListItemText>
            </MenuItem>}

            {!node.selected && <MenuItem onClick={() => {
                nodeContext.select(node.id)
                onClose()
            }}>
                <ListItemIcon>
                    <CheckBox fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Select</ListItemText>
            </MenuItem>}

        </MenuList>
    </Paper>
}