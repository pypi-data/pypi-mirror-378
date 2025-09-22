"""
FastAPI integration example for memhunt

This module demonstrates how to integrate the memory debugging tools
with FastAPI applications.
"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Import our memory debugging tools
from pympler import muppy, summary
import objgraph

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Memory Hunt - FastAPI Edition",
              description="Memory debugging tools for FastAPI applications",
              version="0.2.0")

# Set up templates (you would need to create the template files)
templates = Jinja2Templates(directory="templates")


class MemoryDebugger:
    """Memory debugging utilities adapted for FastAPI"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of current memory usage"""
        try:
            all_objects = muppy.get_objects()
            mem_summary = summary.summarize(all_objects)
            
            return {
                "total_objects": len(all_objects),
                "summary": [
                    {
                        "type": item[0],
                        "count": item[1],
                        "total_size": item[2]
                    }
                    for item in mem_summary[:20]  # Top 20 types
                ],
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Error getting memory summary: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_most_common_types(self) -> Dict[str, Any]:
        """Get most common object types using objgraph"""
        try:
            pairs = objgraph.most_common_types(limit=20)
            return {
                "most_common": [
                    {"type": pair[0], "count": pair[1]}
                    for pair in pairs
                ],
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Error getting common types: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_biggest_memory_users(self) -> Dict[str, Any]:
        """Get biggest memory consumers"""
        try:
            all_objects = muppy.get_objects()
            mem_summary = summary.summarize(all_objects)
            
            # Sort by total size
            sorted_summary = sorted(mem_summary, key=lambda x: x[2],
                                    reverse=True)
            
            return {
                "biggest_users": [
                    {
                        "type": item[0],
                        "count": item[1],
                        "total_size": item[2],
                        "avg_size": item[2] / item[1] if item[1] > 0 else 0
                    }
                    for item in sorted_summary[:10]  # Top 10
                ],
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Error getting biggest users: {e}")
            return {"status": "error", "message": str(e)}


# Initialize the memory debugger
memory_debugger = MemoryDebugger()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main page with links to debugging tools"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Memory Hunt - FastAPI Edition"
    })


@app.get("/api/memory/summary")
async def get_memory_summary() -> Dict[str, Any]:
    """Get memory usage summary"""
    return memory_debugger.get_memory_summary()


@app.get("/api/memory/common-types")
async def get_common_types() -> Dict[str, Any]:
    """Get most common object types"""
    return memory_debugger.get_most_common_types()


@app.get("/api/memory/biggest-users")
async def get_biggest_users() -> Dict[str, Any]:
    """Get biggest memory consumers"""
    return memory_debugger.get_biggest_memory_users()


@app.get("/api/memory/object-refs")
async def get_object_refs(
    object_type: str,
    max_depth: int = 3,
    format: str = "json"
):
    """
    Get reference graph for objects of a specific type
    
    Note: This would generate a graph file in a real implementation
    """
    try:
        # In a real implementation, you'd generate the graph
        # and return either the image or JSON representation
        return {
            "object_type": object_type,
            "max_depth": max_depth,
            "message": ("Reference graph generation not implemented "
                        "in this example"),
            "status": "info"
        }
    except Exception as e:
        logger.error(f"Error generating refs for {object_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/memory", response_class=HTMLResponse)
async def memory_debug_page(request: Request):
    """Memory debugging dashboard"""
    # Get all the memory data
    memory_summary = memory_debugger.get_memory_summary()
    common_types = memory_debugger.get_most_common_types()
    biggest_users = memory_debugger.get_biggest_memory_users()
    
    return templates.TemplateResponse("memory_debug.html", {
        "request": request,
        "memory_summary": memory_summary,
        "common_types": common_types,
        "biggest_users": biggest_users,
        "title": "Memory Debug Dashboard"
    })


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log requests (useful for debugging)"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Status: {response.status_code} | "
        f"Process time: {process_time:.4f}s"
    )
    
    return response


if __name__ == "__main__":
    import time
    
    print("Starting Memory Hunt FastAPI server...")
    print("Visit http://localhost:8000 for the main page")
    print("Visit http://localhost:8000/docs for API documentation")
    print("Visit http://localhost:8000/debug/memory for memory debugging")
    
    uvicorn.run(
        "fastapi_example:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )