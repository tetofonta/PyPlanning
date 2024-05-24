import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import MenuList from '@mui/material/MenuList';
import MenuItem from '@mui/material/MenuItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import {Add, Close, Delete, Edit} from "@mui/icons-material"
import {GraphNode} from "reagraph";
import {NodeContextType, NodeType} from "./NodeContext.tsx";

export type NodeMenuProps = {
    node: GraphNode & { node: NodeType };
    onClose: () => void,
    nodeContext: NodeContextType
};

export const NodeMenu = (props: NodeMenuProps) => {

    const {nodeContext, onClose, node} = props;

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
                    node: NodeType.WAYPOINT,
                    id: Math.random().toString(26).substring(2)
                })
                onClose()
            }}>
                <ListItemIcon>
                    <Add fontSize="small"/>
                </ListItemIcon>
                <ListItemText>New Waypoint</ListItemText>
            </MenuItem>

            {node.node !== NodeType.START && <MenuItem onClick={onClose}>
                <ListItemIcon>
                    <Delete fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Delete Node</ListItemText>
            </MenuItem>}

            <MenuItem onClick={onClose}>
                <ListItemIcon>
                    <Edit fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Edit Node</ListItemText>
            </MenuItem>

        </MenuList>
    </Paper>
}